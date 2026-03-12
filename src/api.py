"""
FastAPI Backend — Groundwater Potential Prediction
Run: uvicorn src.api:app --host 0.0.0.0 --port 8000 --reload
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import pandas as pd
import pickle
import os
from typing import Optional
import csv
from .database import init_db, save_prediction_to_sql, DB_PATH

# ─────────────────────────────────────────────
#  Load model & unique values
# ─────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
# On Vercel, the models directory is relative to the root or current file
MODEL_PATH         = os.path.join(BASE_DIR, "models", "model.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH     = os.path.join(BASE_DIR, "models", "groundwater_model.pkl")
UNIQUE_VALUES_PATH = os.path.join(BASE_DIR, "models", "unique_values.pkl")

model        = None
unique_values = {}

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print("✅ Model loaded.")
except Exception as e:
    print(f"⚠️  Could not load model: {e}")

try:
    with open(UNIQUE_VALUES_PATH, "rb") as f:
        unique_values = pickle.load(f)
    print("✅ Unique values loaded.")
except Exception as e:
    print(f"⚠️  Could not load unique values: {e}")
    unique_values = {
        "Geology":       ["Gneiss", "Schist", "Granite", "Basalt"],
        "Geomorphology": ["Flood Plain", "Pediplain", "Hills"],
        "Soil":          ["Red Soil", "Black Cotton Soil", "Alluvial"],
        "LULC":          ["Agriculture", "Forest", "Water Body"],
    }

# ─────────────────────────────────────────────
#  FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(
    title="Groundwater Potential Prediction API",
    description=(
        "Random Forest ML model for groundwater potential zoning "
        "across the Godavari Basin, Telangana."
    ),
    version="1.0.0",
)

@app.on_event("startup")
def startup_event():
    init_db()

# Allow React (Vite dev) and production domains to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Request / Response schemas
# ─────────────────────────────────────────────
class PredictRequest(BaseModel):
    geology:           str   = Field(..., example="Basalt")
    geomorphology:     str   = Field(..., example="Flood Plain")
    soil:              str   = Field(..., example="Alluvial")
    slope_percent:     float = Field(..., ge=0,  le=100,  example=15.0)
    drainage_density:  float = Field(..., ge=0,  le=10,   example=2.5)
    lineament_density: float = Field(..., ge=0,  le=5,    example=0.5)
    lulc:              str   = Field(..., example="Agriculture")
    ndvi:              float = Field(..., ge=-1, le=1,    example=0.4)
    savi:              float = Field(..., ge=-1, le=1,    example=0.3)
    rainfall_mm:       float = Field(..., ge=0,  le=5000, example=800.0)

class PredictResponse(BaseModel):
    predicted_zone: str
    probabilities:  dict
    model_loaded:   bool

class MetaResponse(BaseModel):
    geology:       list
    geomorphology: list
    soil:          list
    lulc:          list

# ─────────────────────────────────────────────
#  Endpoints
# ─────────────────────────────────────────────
@app.get("/", summary="Health check")
def root():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "message": "Groundwater Prediction API is running. Visit /docs for Swagger UI.",
    }

@app.get("/api/meta", response_model=MetaResponse, summary="Get valid dropdown values")
@app.get("/meta", response_model=MetaResponse, summary="Get valid dropdown values")
def get_meta():
    """Returns the allowed categorical values for the prediction inputs."""
    return {
        "geology":       unique_values.get("Geology", []),
        "geomorphology": unique_values.get("Geomorphology", []),
        "soil":          unique_values.get("Soil", []),
        "lulc":          unique_values.get("LULC", []),
    }

@app.post("/api/predict", response_model=PredictResponse, summary="Predict groundwater zone")
@app.post("/predict", response_model=PredictResponse, summary="Predict groundwater zone")
def predict(data: PredictRequest):
    """
    Submit hydro-geological parameters and get back the predicted
    groundwater potential zone with class probabilities.
    """
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Check server logs.")

    inp = pd.DataFrame([{
        "Geology":           data.geology,
        "Geomorphology":     data.geomorphology,
        "Soil":              data.soil,
        "Slope_percent":     data.slope_percent,
        "Drainage_Density":  data.drainage_density,
        "Lineament_Density": data.lineament_density,
        "LULC":              data.lulc,
        "NDVI":              data.ndvi,
        "SAVI":              data.savi,
        "Rainfall_mm":       data.rainfall_mm,
    }])

    try:
        pred  = model.predict(inp)[0]
        probs = model.predict_proba(inp)[0]
        cls   = model.classes_
        
        response = PredictResponse(
            predicted_zone=str(pred),
            probabilities={str(c): float(round(p, 4)) for c, p in zip(cls, probs)},
            model_loaded=True,
        )
        
        print(f"\n🚀 [BACKEND RESPONSE] Predicted: {response.predicted_zone}")
        print(f"📊 Probabilities: {response.probabilities}\n")
        
        # 💾 SAVE TO CSV & SQL
        storage_data = {
            "geology": data.geology,
            "geomorphology": data.geomorphology,
            "soil": data.soil,
            "slope_percent": data.slope_percent,
            "drainage_density": data.drainage_density,
            "lineament_density": data.lineament_density,
            "lulc": data.lulc,
            "ndvi": data.ndvi,
            "savi": data.savi,
            "rainfall_mm": data.rainfall_mm,
            "predicted_zone": response.predicted_zone,
            "probabilities": response.probabilities
        }
        
        save_prediction_to_csv(storage_data)
        save_prediction_to_sql(storage_data)
        
        return response
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

def save_prediction_to_csv(data: dict):
    """Saves a prediction record to a CSV file."""
    csv_file = os.path.join(os.path.dirname(BASE_DIR), "predictions.csv")
    file_exists = os.path.isfile(csv_file)
    
    try:
        with open(csv_file, mode='a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(data)
        print("✅ Prediction saved to CSV.")
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")

@app.get("/api/history", summary="Get prediction history from SQL")
def get_history():
    """Returns all stored predictions from the SQLite database."""
    if not os.path.exists(DB_PATH):
        return {"history": []}
    
    try:
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM predictions ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return {"history": [dict(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/api/stations", summary="Get all station data")
@app.get("/stations", summary="Get all station data")
def get_stations():
    """Returns static metadata for all Godavari monitoring stations."""
    # Hardcode stations to avoid dependency on src.app which uses Gradio
    STATIONS = {
        "Bhadrachalam":    {
            "lat":17.668,"lon":80.893,"avg_discharge":1340,"peak_discharge":3400,"min_discharge":370,"current_level":46.5,"monsoon_flow":3200,
            "groundwater_zone":"High Potential Zone","aquifer_type":"Basalt with Granitic Gneiss","depth_to_water":8.5,"water_quality":"Good",
            "yield_potential":"High (15-25 lpm)","recharge_rate":"Medium (500-750 mm/year)","density":"Moderate - 1 well/2 ha",
            "soil_type":"Black Soil & Red Soil","geological_formation":"Deccan Basalt & Archean Granite",
            "recommendation":"Suitable for irrigation wells",
            "description": "Known for its historic temple on the banks of the Godavari, this station monitors a critical bend in the river. The groundwater here is influenced by the surrounding basaltic layers, offering moderate to high yield for local agriculture."
        },
        "Ramagundam NTPC": {
            "lat":18.755,"lon":79.513,"avg_discharge":1158,"peak_discharge":3000,"min_discharge":280,"current_level":43.2,"monsoon_flow":2800,
            "groundwater_zone":"Moderate Potential Zone","aquifer_type":"Granite with Quartzite","depth_to_water":12.3,"water_quality":"Good",
            "yield_potential":"Moderate (8-15 lpm)","recharge_rate":"Low (350-500 mm/year)","density":"Low - 1 well/3-4 ha",
            "soil_type":"Red Soil & Laterite","geological_formation":"Archean Granite & Pegmatite",
            "recommendation":"Suitable for domestic wells",
            "description": "Located near one of India's largest power plants, this station tracks water levels in an industrial zone. The groundwater management here is vital for maintaining the balance between industrial cooling needs and domestic availability for nearby townships."
        },
        "Dowleswaram":     {
            "lat":16.934,"lon":81.771,"avg_discharge":1492,"peak_discharge":3700,"min_discharge":410,"current_level":47.5,"monsoon_flow":3500,
            "groundwater_zone":"Very High Potential Zone","aquifer_type":"Alluvium & Basalt","depth_to_water":6.2,"water_quality":"Excellent",
            "yield_potential":"Very High (25-40 lpm)","recharge_rate":"High (750-1000 mm/year)","density":"High - 1 well/1.5 ha",
            "soil_type":"Alluvial Soil","geological_formation":"Recent Alluvium",
            "recommendation":"Highly suitable for large scale irrigation",
            "description": "Site of the famous Cotton Barrage, this location is a hub for irrigation control in the fertile delta region. The alluvium-rich soil here provides exceptional groundwater potential, supporting vast hectares of paddy fields."
        },
        "Pattiseema":      {
            "lat":17.136,"lon":81.609,"avg_discharge":1280,"peak_discharge":3300,"min_discharge":360,"current_level":46.2,"monsoon_flow":3150,
            "groundwater_zone":"High Potential Zone","aquifer_type":"Basalt & Alluvium","depth_to_water":7.8,"water_quality":"Good",
            "yield_potential":"High (18-28 lpm)","recharge_rate":"High (650-850 mm/year)","density":"Moderate-High - 1 well/2 ha",
            "soil_type":"Black Soil & Alluvial","geological_formation":"Deccan Basalt & Alluvium",
            "recommendation":"Suitable for irrigation & domestic use",
            "description": "A modern engineering marvel, this station is part of the first-ever river linking project. It monitors the diversion of Godavari water to the Krishna delta, playing a key role in regional water security and groundwater recharge."
        },
        "Rajahmundry":     {
            "lat":17.000,"lon":81.804,"avg_discharge":1420,"peak_discharge":3620,"min_discharge":395,"current_level":47.2,"monsoon_flow":3400,
            "groundwater_zone":"Very High Potential Zone","aquifer_type":"Alluvium & Basalt","depth_to_water":5.8,"water_quality":"Excellent",
            "yield_potential":"Very High (28-42 lpm)","recharge_rate":"High (780-1050 mm/year)","density":"High - 1 well/1.2 ha",
            "soil_type":"Deep Alluvial Soil","geological_formation":"Recent Alluvium & Basalt",
            "recommendation":"Highly suitable for large-scale irrigation and industrial use",
            "description": "Situated by the widest point of the Godavari, this station overlooks the iconic Rail-cum-Road bridge. The deep alluvial deposits in this area make it one of the most productive groundwater zones in the entire basin."
        },
    }
    return {"stations": STATIONS}

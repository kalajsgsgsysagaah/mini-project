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

# ─────────────────────────────────────────────
#  Load model & unique values
# ─────────────────────────────────────────────
BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH         = os.path.join(BASE_DIR, "models", "groundwater_model.pkl")
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

# Allow Gradio (localhost:7866) to call this API
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

@app.get("/meta", response_model=MetaResponse, summary="Get valid dropdown values")
def get_meta():
    """Returns the allowed categorical values for the prediction inputs."""
    return {
        "geology":       unique_values.get("Geology", []),
        "geomorphology": unique_values.get("Geomorphology", []),
        "soil":          unique_values.get("Soil", []),
        "lulc":          unique_values.get("LULC", []),
    }

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
        return PredictResponse(
            predicted_zone=str(pred),
            probabilities={str(c): float(round(p, 4)) for c, p in zip(cls, probs)},
            model_loaded=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.get("/stations", summary="Get all station data")
def get_stations():
    """Returns static metadata for all Godavari monitoring stations."""
    from src.app import STATIONS
    return {"stations": STATIONS}

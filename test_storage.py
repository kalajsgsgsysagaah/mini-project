import requests
import os
import sqlite3
import pandas as pd
import time

def test_prediction():
    url = "http://localhost:8000/predict"
    payload = {
        "geology": "Basalt",
        "geomorphology": "Flood Plain",
        "soil": "Alluvial",
        "slope_percent": 15.0,
        "drainage_density": 2.5,
        "lineament_density": 0.5,
        "lulc": "Agriculture",
        "ndvi": 0.4,
        "savi": 0.3,
        "rainfall_mm": 800.0
    }
    
    print(f"📡 Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Prediction successful!")
        print(f"Result: {response.json()['predicted_zone']}")
        
        # Give it a second to write to disk
        time.sleep(1)
        
        # Check CSV
        csv_path = "predictions.csv"
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"✅ CSV found! Latest entry:\n{df.tail(1)}")
        else:
            print("❌ CSV not found!")
            
        # Check SQLite
        db_path = "predictions.db"
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df_sql = pd.read_sql_query("SELECT * FROM predictions ORDER BY id DESC LIMIT 1", conn)
            print(f"✅ SQL database found! Latest entry:\n{df_sql}")
            conn.close()
        else:
            print("❌ SQL database not found!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")

if __name__ == "__main__":
    test_prediction()

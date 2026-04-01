import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(os.path.dirname(BASE_DIR), "predictions.db")

def init_db():
    """Initializes the SQLite database and creates the predictions table if it doesn't exist."""
    print(f"🗄️  Initializing database at {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            geology TEXT,
            geomorphology TEXT,
            soil TEXT,
            slope_percent REAL,
            drainage_density REAL,
            lineament_density REAL,
            lulc TEXT,
            ndvi REAL,
            savi REAL,
            rainfall_mm REAL,
            predicted_zone TEXT,
            probabilities TEXT,
            station TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE predictions ADD COLUMN station TEXT")
    except sqlite3.OperationalError:
        pass # column might already exist
    conn.commit()
    conn.close()

def save_prediction_to_sql(data: dict):
    """Saves a prediction record to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (
                geology, geomorphology, soil, slope_percent, 
                drainage_density, lineament_density, lulc, 
                ndvi, savi, rainfall_mm, predicted_zone, probabilities, station
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get("geology"), data.get("geomorphology"), data.get("soil"), 
            data.get("slope_percent"), data.get("drainage_density"), 
            data.get("lineament_density"), data.get("lulc"), 
            data.get("ndvi"), data.get("savi"), data.get("rainfall_mm"), 
            data.get("predicted_zone"), str(data.get("probabilities")), data.get("station")
        ))
        conn.commit()
        conn.close()
        print("✅ Prediction saved to SQL (SQLite).")
    except Exception as e:
        print(f"❌ Error saving to SQL: {e}")

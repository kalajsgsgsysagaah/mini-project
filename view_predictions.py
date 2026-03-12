import sqlite3
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "predictions.db")

def view_predictions():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        # Using pandas for pretty printing table
        df = pd.read_sql_query("SELECT * FROM predictions ORDER BY timestamp DESC", conn)
        conn.close()

        if df.empty:
            print("📭 No predictions found in the database.")
        else:
            print(f"📊 Found {len(df)} predictions:")
            print("-" * 100)
            print(df.to_string(index=False))
            print("-" * 100)
    except Exception as e:
        print(f"❌ Error reading database: {e}")

if __name__ == "__main__":
    view_predictions()

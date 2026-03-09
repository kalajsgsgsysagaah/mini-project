import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score

# Constants
DATA_PATH = r'c:\Users\Gaurav Kalyan\OneDrive\Desktop\mini-project(3-2)\godavari_groundwater_synthetic_dataset.csv'
MODEL_DIR = r'c:\Users\Gaurav Kalyan\OneDrive\Desktop\mini-project(3-2)\src\models'
MODEL_PATH = os.path.join(MODEL_DIR, 'groundwater_model.pkl')

def train():
    # 1. Load Data
    if not os.path.exists(DATA_PATH):
        print(f"Error: Dataset not found at {DATA_PATH}")
        return

    df = pd.read_csv(DATA_PATH)
    print("Data Loaded. Shape:", df.shape)

    # 2. Preprocessing
    # Drop 'Station' as it's an identifier
    if 'Station' in df.columns:
        df = df.drop(columns=['Station'])

    # features and target
    X = df.drop(columns=['Groundwater_Potential_Class'])
    y = df['Groundwater_Potential_Class']

    # Define categorical and numerical columns
    categorical_features = ['Geology', 'Geomorphology', 'Soil', 'LULC']
    numerical_features = ['Slope_percent', 'Drainage_Density', 'Lineament_Density', 'NDVI', 'SAVI', 'Rainfall_mm']

    # Create Preprocessing Pipeline
    # We use OneHotEncoder for categorical features and StandardScaler for numericals
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])

    # Create Model Pipeline
    clf = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    # 3. Data Splitting
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Train
    print("Training Random Forest Model...")
    clf.fit(X_train, y_train)

    # 5. Evaluate
    y_pred = clf.predict(X_test)
    print("Model Evaluation:")
    print(classification_report(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))

    # 6. Save Model
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(clf, f)
    
    print(f"Model saved to {MODEL_PATH}")

    # Also save unique values for categorical features to help build the UI
    unique_values = {col: df[col].unique().tolist() for col in categorical_features}
    with open(os.path.join(MODEL_DIR, 'unique_values.pkl'), 'wb') as f:
        pickle.dump(unique_values, f)
    print("Unique values saved for UI generation.")

if __name__ == "__main__":
    train()

from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="Predictive Maintenance API")

# Load the model
# (Make sure to run main.py locally once to generate this file before deploying)
try:
    model = joblib.load("random_forest_model.pkl")
except Exception as e:
    model = None
    print(f"Failed to load model: {e}")

# This schema should match the 18 features expected by the model.
# Since we used a sliding window, let's accept a flat dictionary of features for simplicity
class Features(BaseModel):
    sensor_1_mean: float = 0.0
    sensor_1_std: float = 0.0
    sensor_1_min: float = 0.0
    sensor_1_max: float = 0.0
    sensor_1_last: float = 0.0
    sensor_1_range: float = 0.0
    sensor_1_trend: float = 0.0
    sensor_1_abs_change: float = 0.0
    sensor_1_variance: float = 0.0
    
    sensor_2_mean: float = 0.0
    sensor_2_std: float = 0.0
    sensor_2_min: float = 0.0
    sensor_2_max: float = 0.0
    sensor_2_last: float = 0.0
    sensor_2_range: float = 0.0
    sensor_2_trend: float = 0.0
    sensor_2_abs_change: float = 0.0
    sensor_2_variance: float = 0.0

@app.get("/api")
def read_root():
    return {"message": "Predictive Maintenance API is running!"}

@app.post("/api/predict")
def predict(data: Features):
    if model is None:
        return {"error": "Model is not loaded."}
    
    # Convert input to DataFrame (to match feature names used during training)
    df = pd.DataFrame([data.dict()])
    
    # Predict
    prediction = model.predict(df)
    probability = model.predict_proba(df)[0].tolist()
    
    return {
        "prediction": int(prediction[0]),
        "probability_failure": probability[1] if len(probability) > 1 else float(prediction[0])
    }

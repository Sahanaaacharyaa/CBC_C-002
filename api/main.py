from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import os
import traceback
import numpy as np

# Paths
BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Load models & preprocessors
risk_model     = joblib.load(os.path.join(MODEL_DIR, "risk_model.pkl"))
comp_model     = joblib.load(os.path.join(MODEL_DIR, "comp_model.pkl"))
scaler         = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
label_encoders = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))

app = FastAPI()

class PatientData(BaseModel):
    Age: int
    Gender_Identity: str
    Surgery_Type: str
    Hormone_Therapy_Duration_Months: int
    Comorbidities: str
    Family_Support: str
    Smoking: str
    Insurance_Status: str
    Mental_Health_PreOp: str
    Mental_Health_Score: float
    Surgeon_Experience_Years: int
    Time_Since_Surgery_Days: int
    Diabetes: int
    HIV: int
    Other_Mental_Health: int

@app.post("/predict")
def predict(data: PatientData):
    try:
        # Build input DataFrame
        df = pd.DataFrame([data.dict()])

        # Encode categorical features using saved label encoders
        for col, le in label_encoders.items():
            if col in df.columns:
                val = df.at[0, col]
                if val not in le.classes_:
                    raise HTTPException(
                        status_code=400,
                        detail=(f"Unrecognized category '{val}' for column '{col}'. "
                                f"Expected one of {list(le.classes_)}")
                    )
                df[col] = le.transform(df[col])

        # ✅ Ensure the correct column order expected by the scaler and models
        expected_order = [
            "Age", "Gender_Identity", "Surgery_Type", "Hormone_Therapy_Duration_Months",
            "Comorbidities", "Family_Support", "Smoking", "Insurance_Status",
            "Mental_Health_PreOp", "Surgeon_Experience_Years",
            "Time_Since_Surgery_Days","Mental_Health_Score", "Diabetes", "HIV", "Other_Mental_Health"
        ]
        df = df[expected_order]

        # Scale the features
        X_scaled = scaler.transform(df)

        # Predict
        risk = risk_model.predict(X_scaled)[0]
        comp = comp_model.predict(X_scaled)[0]

        return {
            "PostOp Risk Level": str(risk),
            "Complications": "Yes" if comp == 1 else "No"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("Error in /predict:", e)
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {e}"
        )

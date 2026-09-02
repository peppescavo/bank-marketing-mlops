from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

app = FastAPI()

project_root = Path(__file__).resolve().parent.parent
model_path = project_root / "models" / "model.joblib"

model = joblib.load(model_path)

class Customer(BaseModel):
    age: int
    job: str
    marital: str
    education: str
    default: str
    housing: str
    loan: str
    contact: str
    month: str
    day_of_week: str
    campaign: int
    pdays: int
    previous: int
    poutcome: str
    emp_var_rate: float
    cons_price_idx: float
    cons_conf_idx: float
    euribor3m: float
    nr_employed: float

    # This tells fastAPI how to build an example
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "age": 42,
                "job": "admin.",
                "marital": "married",
                "education": "university.degree",
                "default": "no",
                "housing": "yes",
                "loan": "no",
                "contact": "cellular",
                "month": "may",
                "day_of_week": "mon",
                "campaign": 1,
                "pdays": 999,
                "previous": 0,
                "poutcome": "nonexistent",
                "emp_var_rate": -1.8,
                "cons_price_idx": 92.893,
                "cons_conf_idx": -46.2,
                "euribor3m": 1.313,
                "nr_employed": 5099.1,
            }
        }
    )

@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(customer: Customer):

    data = pd.DataFrame([{
        "age": customer.age,
        "job": customer.job,
        "marital": customer.marital,
        "education": customer.education,
        "default": customer.default,
        "housing": customer.housing,
        "loan": customer.loan,
        "contact": customer.contact,
        "month": customer.month,
        "day_of_week": customer.day_of_week,
        "campaign": customer.campaign,
        "pdays": customer.pdays,
        "previous": customer.previous,
        "poutcome": customer.poutcome,
        "emp.var.rate": customer.emp_var_rate,
        "cons.price.idx": customer.cons_price_idx,
        "cons.conf.idx": customer.cons_conf_idx,
        "euribor3m": customer.euribor3m,
        "nr.employed": customer.nr_employed,
    }])

    prediction = model.predict(data)[0]
    probability = model.predict_proba(data)[0, 1]

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }
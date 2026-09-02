from pathlib import Path

import joblib
import pandas as pd


def main():
    project_root = Path(__file__).resolve().parent.parent

    model_path = project_root / "models" / "model.joblib"

    model = joblib.load(model_path)

    customer = pd.DataFrame([{
        "age": 40,
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
        "emp.var.rate": -1.8,
        "cons.price.idx": 92.893,
        "cons.conf.idx": -46.2,
        "euribor3m": 1.313,
        "nr.employed": 5099.1,
    }])

    prediction = model.predict(customer)[0]
    probability = model.predict_proba(customer)[0, 1]

    print("Prediction:", prediction)
    print("Probability:", probability)


if __name__ == "__main__":
    main()
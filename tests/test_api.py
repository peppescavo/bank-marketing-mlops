from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict():
    customer = {
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

    response = client.post("/predict", json=customer)

    assert response.status_code == 200

    result = response.json()

    assert result["prediction"] in [0, 1]
    assert 0 <= result["probability"] <= 1


def test_invalid_input():
    response = client.post("/predict", json={"age": 42})

    assert response.status_code == 422
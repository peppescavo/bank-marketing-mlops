# Bank Marketing MLOps

End-to-end machine learning deployment project using the UCI Bank Marketing dataset.

## Goal

Predict whether a bank customer will subscribe to a term deposit using information available before the end of the marketing call.

The focus of this project is not model optimization, but deploying a machine learning model as a production-style service.

## Dataset

UCI Bank Marketing dataset.

Target:

- `1`: customer subscribes to a term deposit
- `0`: customer does not subscribe

The `duration` feature is excluded to avoid using information only available after the call.

## Model

XGBoost classifier.

The preprocessing and model are combined in a scikit-learn Pipeline containing:

- OneHotEncoder for categorical variables
- StandardScaler for numerical variables
- XGBoost classifier

## API

The trained pipeline is exposed through FastAPI.

Endpoints:

- `GET /health`
- `POST /predict`

Interactive API documentation is available at:

`/docs`

## Docker

Build the image:

```bash
docker build -t bank-marketing-api .
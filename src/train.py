from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
)

from xgboost import XGBClassifier

def load_data():
    project_root = Path(__file__).resolve().parent.parent

    data_path = (
        project_root
        / "data"
        / "bank_marketing"
        / "bank_additional"
        / "bank_additional"
        / "bank-additional-full.csv"
    )

    return pd.read_csv(data_path, sep=";")

def split_data(df):
    X = df.drop(columns=["y", "duration"])

    y = df["y"].map({
        'no': 0,
        'yes': 1,
    }).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.15,
        stratify=y,
        random_state=42
    )

    return X_train, X_test, y_train, y_test

def build_pipeline(X_train):
    categorical_columns = X_train.select_dtypes(
        include=["object", "category", "str"]
    ).columns

    numerical_columns = X_train.select_dtypes(
        include=["number"]
    ).columns

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_columns
            ),
            (
                "numerical",
                StandardScaler(),
                numerical_columns
            )
        ]
    )

    model = XGBClassifier(
        max_depth=4,
        learning_rate=0.03,
        n_estimators=200,
        subsample=0.8,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42
    )

    pipeline = Pipeline([
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    return pipeline

def train_model(pipeline, X_train, y_train):
    pipeline.fit(X_train, y_train)

    return pipeline

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "pr_auc": average_precision_score(y_test, y_proba),
    }

    return metrics

def save_artifacts(model, metrics):
    project_root = Path(__file__).resolve().parent.parent

    models_dir = project_root / "models"
    metrics_dir = project_root / "metrics"

    models_dir.mkdir(exist_ok=True)
    metrics_dir.mkdir(exist_ok=True)

    model_path = models_dir / "model.joblib"
    metrics_path = metrics_dir / "final_metrics.json"

    joblib.dump(model, model_path)

    with open(metrics_path, "w") as file:
        json.dump(metrics, file, indent=4)

def main():

    df = load_data()

    X_train, X_test, y_train, y_test = split_data(df)

    pipeline = build_pipeline(X_train)

    model = train_model(
        pipeline,
        X_train,
        y_train,
        )

    metrics = evaluate_model(
        model,
        X_test,
        y_test
    )

    save_artifacts(
        model,
        metrics
    )

if __name__ == "__main__":
    main()
# src/taxi_fare_prediction/pipelines/serve/nodes.py

import pandas as pd
from sklearn.model_selection import train_test_split
from autogluon.tabular import TabularPredictor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score


def load_neuralnettorch_predictor(model_dir: str) -> TabularPredictor:
    return TabularPredictor.load(model_dir)


def split_for_serving(
        df: pd.DataFrame,
        target: str,
        test_size: float,
        random_state: int
) -> pd.DataFrame:
    X = df.drop(columns=[target])
    y = df[target]
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    df_test = X_test.copy()
    df_test[target] = y_test
    return df_test


def load_autogluon_predictor(model_dir: str) -> TabularPredictor:
    return TabularPredictor.load(model_dir)


def make_predictions(
        predictor: TabularPredictor,
        df: pd.DataFrame,
        target: str,
        model_name: str = None  # ← domyślnie brak
) -> pd.DataFrame:
    df_out = df.copy()
    X = df_out.drop(columns=[target], errors="ignore")
    if model_name:
        preds = predictor.predict(X, model=model_name)
    else:
        preds = predictor.predict(X)
    df_out[f"predicted_{target}"] = preds
    return df_out


def evaluate_predictions(
        predictions: pd.DataFrame,
        target: str
) -> pd.DataFrame:
    y_true = predictions[target]
    y_pred = predictions[f"predicted_{target}"]

    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)

    print(f"🔍 RMSE na zestawie testowym: {rmse:.4f}")
    print(f"🔍 MAE  na zestawie testowym: {mae:.4f}")
    print(f"🔍 R²   na zestawie testowym: {r2:.4f}")

    return pd.DataFrame({
        "metric": ["rmse", "mae", "r2"],
        "value": [rmse, mae, r2]
    })

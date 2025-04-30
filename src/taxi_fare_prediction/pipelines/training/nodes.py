# src/taxi_fare_prediction/pipelines/training/nodes.py
import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn.model_selection import train_test_split


def train_autogluon_model(
    df: pd.DataFrame,
    label: str,
    output_dir: str,
    time_limit: int,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple:
    """
    1) Wyświetla macierz korelacji cech (bez kolumny target).
    2) Dzieli df na train/test.
    3) Trenuje AutoGluon tylko na train.
    Zwraca (predictor, df_test).
    """
    # 1. Korelacja
    df_num = df.select_dtypes(include=["number"]).drop(columns=[label], errors="ignore")
    corr = df_num.corr()
    print("📊 Macierz korelacji cech (bez targetu):\n", corr, "\n")

    # 2. Split
    train_df, test_df = train_test_split(
        df, test_size=test_size, random_state=random_state
    )
    print(f"▶️  Rozmiar train: {len(train_df)} wierszy, test: {len(test_df)} wierszy\n")

    # 3. Trening AutoGluon
    predictor = TabularPredictor(
        label=label,
        path=output_dir,
        eval_metric='root_mean_squared_error'
    ).fit(
        train_data=train_df,
        time_limit=time_limit,
        presets='best_quality'
    )

    return predictor, test_df


def evaluate_autogluon_model(
    predictor: TabularPredictor,
    df_test: pd.DataFrame
) -> dict:
    """
    Ewaluacja modelu na df_test.
    Zwraca dict z metrykami (i wypisuje je).
    """
    print("🔍 Ewaluacja na zbiorze testowym:")
    results = predictor.evaluate(df_test, auxiliary_metrics=True)
    return results

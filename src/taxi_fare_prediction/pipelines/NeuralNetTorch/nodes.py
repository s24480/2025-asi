# src/taxi_fare_prediction/pipelines/neuralnettorch/node.py
import pandas as pd
from autogluon.tabular import TabularPredictor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

def train_neuralnettorch_predictor(
    df: pd.DataFrame,
    target: str,
    output_dir: str,
    time_limit: int = None,
    test_size: float = 0.2,
    random_state: int = 42
) -> tuple[TabularPredictor, pd.DataFrame]:
    """
    Dzieli na train/test, trenuje tylko NN_TORCH i zwraca predictor + df_test.
    """
    # rozbijamy:
    X = df.drop(columns=[target])
    y = df[target]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    train_df = X_train.copy()
    train_df[target] = y_train
    test_df  = X_test.copy()
    test_df[target]  = y_test

    # trenujemy wyłącznie NN_TORCH:
    predictor = TabularPredictor(label=target, path=output_dir).fit(
        train_data=train_df,
        time_limit=time_limit,
        hyperparameters={'NN_TORCH': {}}
    )
    return predictor, test_df

def evaluate_neuralnettorch_model(
    predictor: TabularPredictor,
    df_test: pd.DataFrame
) -> pd.DataFrame:
    X_test = df_test.drop(columns=[predictor.label])
    y_true = df_test[predictor.label]
    y_pred = predictor.predict(X_test)

    rmse = mean_squared_error(y_true, y_pred, squared=False)
    mae  = mean_absolute_error(y_true, y_pred)
    r2   = r2_score(y_true, y_pred)

    print(f"🔍 NN-Torch RMSE: {rmse:.4f}")
    print(f"🔍 NN-Torch MAE:  {mae:.4f}")
    print(f"🔍 NN-Torch R²:   {r2:.4f}")

    return pd.DataFrame({
        "metric": ["rmse", "mae", "r2"],
        "value":  [rmse, mae, r2]
    })

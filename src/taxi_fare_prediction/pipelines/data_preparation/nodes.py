# src/data_preparation/nodes.py

import pandas as pd

def remove_outliers(df: pd.DataFrame, column: str, method: str = 'iqr', factor: float = 1.5) -> pd.DataFrame:
    if method == 'iqr':
        q1 = df[column].quantile(0.25)
        q3 = df[column].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - factor * iqr
        upper_bound = q3 + factor * iqr
        df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    else:
        raise ValueError("Obsługiwana jest tylko metoda 'iqr'")
    return df

def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    columns_to_clean = ["trip_distance", "fare_amount", "duration"]
    for col in columns_to_clean:
        df = remove_outliers(df, col, method="iqr", factor=1.5)
    return df

def sample_dataset(df: pd.DataFrame, sample_fraction: float = 0.05) -> pd.DataFrame:
    return df.sample(frac=sample_fraction, random_state=42)

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = clean_dataset(df)
    df_sampled = sample_dataset(df_clean, sample_fraction=0.05)
    return df_sampled

def compute_feature_correlation(
    df: pd.DataFrame,
    target: str
) -> pd.DataFrame:
    """
    Zwraca macierz korelacji pomiędzy cechami (bez kolumny target).
    """
    # wybieramy tylko kolumny numeryczne i usuwamy target
    df_num = df.select_dtypes(include="number").drop(columns=[target], errors="ignore")
    corr = df_num.corr()
    return corr

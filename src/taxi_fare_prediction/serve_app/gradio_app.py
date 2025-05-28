import gradio as gr
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
from typing import Optional, Tuple
from autogluon.tabular import TabularPredictor
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

# Ustal katalog projektu i modelu
ROOT_DIR = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT_DIR / "models" / "neuralnettorch"
PORT = int(os.getenv("PORT", "7860"))

# Cache loadera modelu
_model_cache = {}


def load_neuralnettorch_predictor(model_dir: str) -> TabularPredictor:
    return TabularPredictor.load(model_dir)


def make_predictions(
        predictor,
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


def get_model() -> 'TabularPredictor':  # type: ignore
    path = str(MODEL_DIR)
    if path not in _model_cache:
        _model_cache[path] = load_neuralnettorch_predictor(path)
    return _model_cache[path]


def compute_distance(origin: str, destination: str) -> Optional[float]:
    """
    Geokoduje adresy i zwraca odległość w kilometrach lub None.
    """
    geolocator = Nominatim(user_agent="taxi_fare_app", timeout=10)
    loc1 = geolocator.geocode(origin)
    loc2 = geolocator.geocode(destination)
    if loc1 is None or loc2 is None:
        return None
    return geodesic((loc1.latitude, loc1.longitude), (loc2.latitude, loc2.longitude)).km


def predict_fare(
        passengers: int,
        origin: str,
        destination: str,
        payment: str
) -> Tuple[str, Optional[str]]:
    # Oblicz dystans
    distance = compute_distance(origin, destination)
    if distance is None:
        return "Nie znaleziono jednego z adresów.", None

    # Estymacja czasu (s) przy 30 km/h
    duration = distance / 30 * 3600

    # Przygotowanie danych
    df = pd.DataFrame([{
        "trip_distance": distance,
        "passenger_count": passengers,
        "payment_type": payment,
        "duration": duration
    }])

    # Wczytaj model
    try:
        predictor = get_model()
    except Exception as e:
        return f"Błąd ładowania modelu: {e}", None

    # Predykcja
    try:
        preds = make_predictions(predictor, df, target="fare_amount")
        price = float(preds["predicted_fare_amount"].iloc[0])
        dist_str = f"Odległość: {distance:.2f} km"
        dur_str = f"Szacowany czas: {duration / 60:.1f} min"
        price_str = f"Szacowana cena: {price:.2f}"
        return f"{dist_str}, {dur_str}", price_str
    except Exception as e:
        return f"Błąd podczas predykcji: {e}", None


def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("# Taxi Fare Prediction (Gradio)")
        with gr.Row():
            passengers_slider = gr.Slider(1, 5, value=1, step=1, label="Ilość pasażerów")
            payment_radio = gr.Radio(["card", "cash"], label="Płatność")
        origin_text = gr.Textbox(label="Skąd (adres)")
        destination_text = gr.Textbox(label="Dokąd (adres)")
        btn = gr.Button("Oblicz trasę i cenę")
        distance_out = gr.Textbox(label="Odległość ")
        price_out = gr.Textbox(label="Cena ")

        btn.click(
            fn=predict_fare,
            inputs=[passengers_slider, origin_text, destination_text, payment_radio],
            outputs=[distance_out, price_out]
        )
    return demo


if __name__ == "__main__":
    # Walidacja istnienia modelu
    if not MODEL_DIR.exists():
        raise FileNotFoundError(f"Katalog modelu nie istnieje: {MODEL_DIR}")
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=PORT)

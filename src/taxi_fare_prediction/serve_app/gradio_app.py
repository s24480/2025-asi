import gradio as gr
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
from typing import Optional, Tuple
import pandas as pd

# --------------------------------------------------
# Konfiguracja środowiska
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Geokoder - instancja globalna, by nie tworzyć za każdym razem
# --------------------------------------------------
geolocator = Nominatim(user_agent="taxi_fare_app", timeout=10)

def compute_distance(origin: str, destination: str) -> Optional[float]:
    try:
        a = geolocator.geocode(origin)
        b = geolocator.geocode(destination)
    except Exception:
        return None
    if not a or not b:
        return None
    return geodesic((a.latitude, a.longitude), (b.latitude, b.longitude)).km

# --------------------------------------------------
# Logika predykcji z modelu AutoGluon
# --------------------------------------------------
from autogluon.tabular import TabularPredictor

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    r"C:\Users\Pithe\Documents\GitHub\2025-asi\src\taxi_fare_prediction\pipelines\data_preparation\models\synthetic_taxi_pln"
)
predictor = TabularPredictor.load(MODEL_PATH)

def predict_fare(
    passengers: int,
    origin: str,
    destination: str,
    payment: str
) -> Tuple[str, str]:
    dist_km = compute_distance(origin, destination)
    if dist_km is None:
        return "Nie znaleziono jednego z adresów.", "---"

    # Szacowany czas w minutach
    duration_min = dist_km / 30 * 60

    # Przygotowujemy DataFrame z dokładnymi nazwami kolumn,
    # jakich oczekuje model:
    features = pd.DataFrame([{
        "trip_distance": dist_km,
        "duration": duration_min,
        "passenger_count": passengers,
        # możesz zostawić string lub liczbę 0/1 – w zależności od tego
        # jak model trenowałeś:
        "payment_type": payment
    }])

    # Wywołanie predykcji
    model_pred = predictor.predict(features)[0]
    price_model = f"{model_pred:.2f} zł"

    info_str = f"Odległość: {dist_km:.2f} km, Czas: {duration_min:.1f} min"
    return info_str, price_model


# --------------------------------------------------
# Interfejs Gradio
# --------------------------------------------------
def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("# Taxi Fare Prediction (Gradio)")

        with gr.Row():
            passengers = gr.Slider(1, 5, value=1, step=1, label="Ilość pasażerów")
            payment   = gr.Radio(["card","cash"], value="card", label="Płatność")

        origin      = gr.Textbox(label="Skąd (adres)")
        destination = gr.Textbox(label="Dokąd (adres)")

        btn      = gr.Button("Oblicz trasę i cenę")
        out_dist = gr.Textbox(label="Odległość i czas")
        out_fare = gr.Textbox(label="Cena")

        btn.click(
            fn=predict_fare,
            inputs=[passengers, origin, destination, payment],
            outputs=[out_dist, out_fare]
        )

    return demo

if __name__ == "__main__":
    server_port = int(os.getenv("PORT", "7861"))
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=server_port, share=False)

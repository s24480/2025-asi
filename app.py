import os

import gradio as gr
import pandas as pd

from dotenv import load_dotenv
from typing import Tuple

from geolocation import calculate_full_route_info
from model import download_and_load_autogluon_model

load_dotenv()

predictor = download_and_load_autogluon_model(
    os.getenv("BLOB_CONNECTION_STRING"),
    os.getenv("BLOB_CONTAINER_NAME"),
    os.getenv("BLOB_NAME"),
)


def _predict_fare(
        passengers: int,
        origin: str,
        destination: str,
        payment: str
) -> Tuple[str, str]:
    route_info = calculate_full_route_info(origin, destination)
    duration_minutes = route_info['duration_minutes']
    distance_km = route_info['distance_km']

    if duration_minutes is None or distance_km is None:
        return "Niestety nie udało się odnaleźć trasy.", "---"

    if distance_km > 50:
        return "Trasa nie może być dłuższa niż 50 km.", "---"

    features = pd.DataFrame([{
        "trip_distance": distance_km,
        "duration": duration_minutes,
        "passenger_count": passengers,
        "payment_type": payment
    }])

    model_pred = predictor.predict(features)[0]
    price_model = f"{model_pred:.2f} zł"

    info_str = f"Odległość: {distance_km:.2f} km, Czas: {duration_minutes:.1f} min"
    return info_str, price_model


def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("# Predykcja kosztu za przejazd taksówką")

        with gr.Row():
            passengers = gr.Slider(1, 5, value=1, step=1, label="Ilość pasażerów")
            payment = gr.Radio(["card", "cash"], value="card", label="Płatność")

        origin = gr.Textbox(label="Skąd (adres)")
        destination = gr.Textbox(label="Dokąd (adres)")

        btn = gr.Button("Oblicz trasę i cenę")
        out_dist = gr.Textbox(label="Odległość i czas")
        out_fare = gr.Textbox(label="Cena")

        btn.click(
            fn=_predict_fare,
            inputs=[passengers, origin, destination, payment],
            outputs=[out_dist, out_fare]
        )

    return demo


if __name__ == "__main__":
    server_port = int(os.getenv("PORT", "7861"))
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=server_port, share=False)

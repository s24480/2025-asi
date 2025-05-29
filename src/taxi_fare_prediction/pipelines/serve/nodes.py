# gradio_app.py

import gradio as gr
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os
from dotenv import load_dotenv
from typing import Optional, Tuple

# --------------------------------------------------
# Konfiguracja środowiska
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# Parametry taryfy (zmieniaj według potrzeb)
# --------------------------------------------------
BASE_FARE    = 5.00    # opłata początkowa (zł)
RATE_PER_KM  = 2.50    # zł za każdy kilometr
RATE_PER_MIN = 0.50    # zł za każdą minutę jazdy/postoju

# --------------------------------------------------
# Geokoder - instancja globalna, by nie tworzyć za każdym razem
# --------------------------------------------------
geolocator = Nominatim(user_agent="taxi_fare_app", timeout=10)

# --------------------------------------------------
# Funkcje pomocnicze
# --------------------------------------------------
def compute_distance(origin: str, destination: str) -> Optional[float]:
    """
    Geokoduje adresy i zwraca odległość w kilometrach lub None.
    """
    try:
        a = geolocator.geocode(origin)
        b = geolocator.geocode(destination)
    except Exception:
        return None
    if not a or not b:
        return None
    return geodesic((a.latitude, a.longitude), (b.latitude, b.longitude)).km


def compute_fare(distance_km: float, duration_s: float) -> float:
    """
    Oblicza cenę na podstawie dystansu i czasu.
    """
    minutes = duration_s / 60
    return BASE_FARE + RATE_PER_KM * distance_km + RATE_PER_MIN * minutes

# --------------------------------------------------
# Logika predykcji
# --------------------------------------------------
def predict_fare(
    passengers: int,
    origin: str,
    destination: str,
    payment: str
) -> Tuple[str, str]:
    """
    Zwraca opis dystansu i czasu oraz obliczoną cenę w formacie tekstowym.
    """
    dist = compute_distance(origin, destination)
    if dist is None:
        return ("Nie znaleziono jednego z adresów.", "---")

    # Szacowany czas przy 30 km/h (sekundy)
    duration = dist / 30 * 3600

    # Obliczenie ceny
    fare = compute_fare(dist, duration)

    dist_str   = f"Odległość: {dist:.2f} km"
    time_str   = f"Szacowany czas: {duration/60:.1f} min"
    price_str  = f"Szacowana cena: {fare:.2f} zł"

    return (f"{dist_str}, {time_str}", price_str)

# --------------------------------------------------
# Interfejs Gradio
# --------------------------------------------------
def build_interface() -> gr.Blocks:
    with gr.Blocks() as demo:
        gr.Markdown("# Taxi Fare Prediction (Gradio)")

        with gr.Row():
            passengers = gr.Slider(
                minimum=1,
                maximum=5,
                value=1,
                step=1,
                label="Ilość pasażerów"
            )
            payment = gr.Radio(
                choices=["card", "cash"],
                value="card",
                label="Płatność"
            )

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
    server_port = int(os.getenv("PORT", "7860"))
    demo = build_interface()
    demo.launch(
        server_name="0.0.0.0",  # dostępne lokalnie
        server_port=server_port,
        share=False              # ustaw na True, jeśli chcesz publiczny link
    )

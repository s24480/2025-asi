# gradio_app.py

import gradio as gr
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import os, sys
from dotenv import load_dotenv
from typing import Optional, Tuple

# --------------------------------------------------
# Setup
# --------------------------------------------------
load_dotenv()
# wymusimy niebuforowane stdout
sys.stdout.reconfigure(line_buffering=True)

# --------------------------------------------------
# Taryfa
# --------------------------------------------------
BASE_FARE    = 5.00
RATE_PER_KM  = 2.50
RATE_PER_MIN = 0.50

geolocator = Nominatim(user_agent="taxi_fare_app", timeout=10)

# --------------------------------------------------
# Funkcje z PRINTami
# --------------------------------------------------
def compute_distance(origin: str, destination: str) -> Optional[float]:
    print(f"[PRINT] compute_distance: {origin} → {destination}", flush=True)
    try:
        a = geolocator.geocode(origin)
        b = geolocator.geocode(destination)
    except Exception as e:
        print(f"[PRINT] geocode exception: {e}", flush=True)
        return None
    print(f"[PRINT] geo results: {a}, {b}", flush=True)
    if not a or not b:
        return None
    dist = geodesic((a.latitude, a.longitude), (b.latitude, b.longitude)).km
    print(f"[PRINT] dist = {dist}", flush=True)
    return dist

def compute_fare(dist: float, dur_s: float) -> float:
    print(f"[PRINT] compute_fare: dist={dist}, dur_s={dur_s}", flush=True)
    fare = BASE_FARE + RATE_PER_KM * dist + RATE_PER_MIN * (dur_s/60)
    print(f"[PRINT] fare = {fare}", flush=True)
    return fare

def predict_fare(
    passengers: int,
    origin: str,
    destination: str,
    payment: str
) -> Tuple[str, str]:
    print("🚀 [PRINT] predict_fare called 🚀", flush=True)
    print(f"[PRINT] inputs: passengers={passengers}, pay={payment}", flush=True)
    dist = compute_distance(origin, destination)
    if dist is None:
        return "Nie znaleziono jednego z adresów.", "---"
    dur = dist/30*3600
    print(f"[PRINT] dur = {dur}", flush=True)
    fare = compute_fare(dist, dur)
    out1 = f"Odległość: {dist:.2f} km, czas: {dur/60:.1f} min"
    out2 = f"Cena: {fare:.2f} zł"
    print(f"[PRINT] returning: {out1}  |  {out2}", flush=True)
    return out1, out2

# --------------------------------------------------
# Gradio Interface
# --------------------------------------------------
inputs = [
    gr.Slider(1, 5, step=1, value=1, label="Ilość pasażerów"),
    gr.Textbox(label="Skąd (adres)"),
    gr.Textbox(label="Dokąd (adres)"),
    gr.Radio(["card","cash"], value="card", label="Płatność")
]
outputs = [
    gr.Textbox(label="Odległość i czas"),
    gr.Textbox(label="Cena")
]

if __name__ == "__main__":
    print("=== START gradio_app.py (Interface) ===", flush=True)
    demo = gr.Interface(
        fn=predict_fare,
        inputs=inputs,
        outputs=outputs,
        title="Taxi Fare Prediction",
        description="Oblicza cenę taksówki wg prostej taryfy z debugiem"
    )
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT","7860")), debug=True)

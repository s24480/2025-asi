# src/taxi_fare_prediction/pipelines/serve/pipeline.py
from kedro.pipeline import Pipeline, node
from .nodes import split_for_serving, load_neuralnettorch_predictor, make_predictions, evaluate_predictions
from .nodes import compute_fare, compute_distance  # dopisz

def predict_node(df, passengers, origin, destination, payment):
    # tego użyje frontend Kedro–Gradio
    dist = compute_distance(origin, destination)
    if dist is None:
        return "Nie znaleziono adresu", ""
    duration = dist / 30 * 3600
    fare = compute_fare(dist, duration)
    return f"Odległość: {dist:.2f} km, czas: {duration/60:.1f} min", f"{fare:.2f} zł"

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline([
        # … (dotychczasowe węzły split, load, evaluate jeśli chcesz zostawić)
        node(
            func=predict_node,
            inputs=[
                "serve_test_data",             # lub: parametry passengers, origin, destination, payment
                "params:serve.frontend.passengers",
                "params:serve.frontend.origin",
                "params:serve.frontend.destination",
                "params:serve.frontend.payment",
            ],
            outputs=["out_dist", "out_fare"],
            name="serve_formula_node"
        )
    ])

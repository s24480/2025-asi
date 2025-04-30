# src/taxi_fare_prediction/pipelines/neuralnettorch/pipeline.py
from kedro.pipeline import Pipeline, node
from .nodes import train_neuralnettorch_predictor, evaluate_neuralnettorch_model

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_neuralnettorch_predictor,
                inputs=[
                    "taxi-ds-cleaned",
                    "params:autogluon.target",
                    "params:autogluon.output_dir",
                    "params:autogluon.time_limit",
                    "params:NeuralNetTorch.test_size",      # ← potrzebne tu
                    "params:NeuralNetTorch.random_state",  # ← i tu
                ],
                outputs=["neuralnettorch_predictor", "neuralnettorch_df_test"],
                name="train_neuralnettorch_node",
            ),
            node(
                func=evaluate_neuralnettorch_model,
                inputs=["neuralnettorch_predictor", "neuralnettorch_df_test"],
                outputs="neuralnettorch_metrics",
                name="evaluate_neuralnettorch_node",
            ),
        ]
    )

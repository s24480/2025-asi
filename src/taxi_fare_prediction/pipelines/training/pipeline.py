# src/taxi_fare_prediction/pipelines/training/pipeline.py
from kedro.pipeline import Pipeline, node
from .nodes import train_autogluon_model, evaluate_autogluon_model

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=train_autogluon_model,
                inputs=[
                    "taxi-ds-cleaned",
                    "params:autogluon.target",
                    "params:autogluon.output_dir",
                    "params:autogluon.time_limit",
                    "params:model_train.test_size",
                    "params:model_train.random_state",
                ],
                outputs=["autogluon_predictor", "df_test"],
                name="train_autogluon_model_node",
            ),
            node(
                func=evaluate_autogluon_model,
                inputs=["autogluon_predictor", "df_test"],
                outputs="autogluon_metrics",
                name="evaluate_autogluon_model_node",
            ),
        ]
    )

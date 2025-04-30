# src/taxi_fare_prediction/pipelines/serve/pipeline.py
from kedro.pipeline import Pipeline, node
from .nodes import split_for_serving, load_neuralnettorch_predictor, make_predictions, evaluate_predictions

def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            # 1) robimy split na serve_test_data
            node(
                func=split_for_serving,
                inputs=[
                    "taxi-ds-cleaned",
                    "params:autogluon.target",
                    "params:serve.test_size",
                    "params:serve.random_state",
                ],
                outputs="serve_test_data",
                name="split_for_serving_node",
            ),

            # 2) wczytujemy model NN-Torch, który wcześniej zapisałeś
            node(
                func=load_neuralnettorch_predictor,
                inputs="params:autogluon.output_dir",
                outputs="neuralnettorch_predictor_served",
                name="load_neuralnettorch_model_node",
            ),
            node(
                func=make_predictions,
                inputs=[
                    "neuralnettorch_predictor_served",
                    "serve_test_data",
                    "params:autogluon.target",
                ],
                outputs="predictions",
                name="serve_model_node",
            ),

            # 4) liczymy metryki
            node(
                func=evaluate_predictions,
                inputs=["predictions", "params:autogluon.target"],
                outputs="model_metrics",
                name="evaluate_predictions_node",
            ),
        ]
    )

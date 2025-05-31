"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.12
"""
# src/data_preparation/pipeline.py
from kedro.pipeline import node, Pipeline, pipeline
from .nodes import prepare_data,compute_feature_correlation

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=prepare_data,
            inputs="taxi-ds",
            outputs="taxi-ds-cleaned",
            name="data_preparation"
        )
    ])

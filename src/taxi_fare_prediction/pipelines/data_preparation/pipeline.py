"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.12
"""
# src/data_preparation/pipeline.py
from kedro.pipeline import node, Pipeline, pipeline
import pandas as pd
from .nodes import prepare_data,compute_feature_correlation

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=prepare_data,
            inputs="taxi-ds",                # nazwa datasetu wejściowego z catalog.yml
            outputs="taxi-ds-cleaned",   # nazwa datasetu wyjściowego z catalog.yml
            name="data_preparation"
        ),
        node(
            func=compute_feature_correlation,
            inputs=["taxi-ds-cleaned", "params:autogluon.target"],
            outputs="feature_correlation",
            name="compute_corr_node",
        )
    ])

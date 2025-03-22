"""
This is a boilerplate pipeline 'data_preparation'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline
import pandas as pd
from .nodes import prepare_data

def create_pipeline(**kwargs) -> Pipeline:
    return pipeline([
        node(
            func=prepare_data,
            inputs="taxi-ds",                # nazwa datasetu wejściowego z catalog.yml
            outputs="taxi-ds-cleaned",   # nazwa datasetu wyjściowego z catalog.yml
            name="data_preparation_node"
        )
    ])

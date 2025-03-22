"""Project pipelines."""

from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline
from .pipelines import data_preparation

def register_pipelines() -> dict[str, Pipeline]:
    pipelines = find_pipelines()
    pipelines["__default__"] = sum(pipelines.values())
    pipelines["data_processing"] = data_preparation
    return pipelines

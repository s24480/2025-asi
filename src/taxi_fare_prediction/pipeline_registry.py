from kedro.framework.project import find_pipelines
from kedro.pipeline import Pipeline

# zamiast importować moduły:
# from .pipelines import serve, NeuralNetTorch
# importuj ich funkcje create_pipeline:
from .pipelines.serve.pipeline import create_pipeline as serve_pipeline
from .pipelines.NeuralNetTorch.pipeline import create_pipeline as nn_pipeline
from .pipelines.data_preparation.pipeline import create_pipeline as prep_pipeline
from .pipelines.training.pipeline import create_pipeline as train_pipeline

def register_pipelines() -> dict[str, Pipeline]:
    # jeśli chcesz wykorzystać automatyczne find_pipelines, możesz,
    # ale poniżej pokazuję ręczne wiązanie dla pełnej kontroli:
    pipelines: dict[str, Pipeline] = {
        "data_preparation": prep_pipeline(),
        "training":       train_pipeline(),
        "serve":          serve_pipeline(),
        "neural_net":     nn_pipeline(),
    }
    # __default__ może być sumą wszystkich, albo tylko tych, które chcesz
    pipelines["__default__"] = (
        pipelines["data_preparation"]
        + pipelines["training"]
        + pipelines["neural_net"]
        + pipelines["serve"]
    )
    return pipelines

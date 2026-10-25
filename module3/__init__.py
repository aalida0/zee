"""General complex Zee scalar LFV components. No global exclusion decision."""


def evaluate(data):
    from .interface import evaluate as run
    return run(data)

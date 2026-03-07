class PredictionEngineError(Exception):
    """Base exception for prediction engine errors."""

    pass


class PredictionContextError(PredictionEngineError):
    """Exception raised when there is an error in the prediction context or input."""

    pass

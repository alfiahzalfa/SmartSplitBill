from enum import Enum
from typing import Type

from modules.data import session_data
from modules.utils import SettingsError

from .base import AIModel
from .donut import DonutModel
from .gemini import GeminiModel
from .groq import GroqModel


class ModelNames(Enum):
    """Nama-nama model AI yang tersedia."""
    GEMINI = "Gemini"
    GROQ = "Groq"
    DONUT = "Donut (Lokal)"


MODELS_LOADER: dict[ModelNames, Type[AIModel]] = {
    ModelNames.GEMINI: GeminiModel,
    ModelNames.GROQ: GroqModel,
    ModelNames.DONUT: DonutModel,
}


def _load_model() -> AIModel:
    model_name = session_data.model_name.get()
    if model_name not in MODELS_LOADER:
        raise SettingsError(f"Model '{model_name}' tidak dikenali.")
    return MODELS_LOADER[model_name]()


def get_model() -> AIModel:
    model = session_data.model.get()
    if model is None:
        model = _load_model()
        session_data.model.set(model)
    return model
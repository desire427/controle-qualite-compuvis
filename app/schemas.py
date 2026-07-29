"""
Schemas Pydantic : contrat de sortie de l'API, separe de la logique metier.
"""
from pydantic import BaseModel


class InspectionResult(BaseModel):
    status: str          # "conforme" ou "defaut"
    confidence: float    # score de confiance du diagnostic retenu
    label_detail: str    # description textuelle la plus proche selon le modele
    filename: str
    file_size: int
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str


class ErrorResponse(BaseModel):
    error: str

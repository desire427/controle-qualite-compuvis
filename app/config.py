"""
Configuration centralisee du service.
Toutes les valeurs sont surchargeables via variables d'environnement (.env),
conformement au critere "gerer proprement les variables d'environnement".
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Modele Hugging Face utilise pour l'inference (voir README pour la justification)
    MODEL_NAME: str = os.getenv("MODEL_NAME", "openai/clip-vit-base-patch32")

    # Taille max acceptee pour une image, en octets (5 Mo par defaut)
    MAX_IMAGE_SIZE: int = int(os.getenv("MAX_IMAGE_SIZE", str(5 * 1024 * 1024)))

    # Au-dessus de ce score, le diagnostic "defaut" est considere fiable
    DEFECT_CONFIDENCE_THRESHOLD: float = float(os.getenv("DEFECT_CONFIDENCE_THRESHOLD", "0.55"))

    # "cpu" ou "cuda" selon la machine cible (voir README : ce modele tourne bien en CPU)
    DEVICE: str = os.getenv("DEVICE", "cpu")

    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


settings = Settings()

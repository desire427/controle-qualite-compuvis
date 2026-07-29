"""
Point d'entree FastAPI.
Ce fichier ne contient QUE le routage HTTP : la validation, la config et
l'inference vivent dans leurs modules dedies (separation des responsabilites).
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import InspectionResult, HealthResponse, ErrorResponse
from app.validators import validate_extension, validate_magic_bytes, read_upload_within_limit
from app.vision_service import VisionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(
    title="Controle Qualite Automatise",
    description="Micro-service de detection de defauts sur produits manufactures (vision par ordinateur)",
    version="2.0.0",
)

vision_service: Optional[VisionService] = None


@app.on_event("startup")
async def load_model() -> None:
    global vision_service
    vision_service = VisionService(model_name=settings.MODEL_NAME, device=settings.DEVICE)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Uniformise toutes les erreurs HTTP au format {"error": ...} attendu par le sujet."""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.get("/", tags=["Info"])
async def root():
    return {
        "service": "Controle Qualite Automatise",
        "version": "2.0.0",
        "status": "online",
        "model": settings.MODEL_NAME,
        "endpoints": {
            "/inspect-image": "POST - Analyser une image (multipart/form-data)",
            "/health": "GET - Verifier l'etat du service",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Info"])
async def health_check():
    return HealthResponse(
        status="healthy",
        model_loaded=vision_service is not None,
        timestamp=datetime.now().isoformat(),
    )


@app.post(
    "/inspect-image",
    response_model=InspectionResult,
    responses={
        400: {"model": ErrorResponse},
        413: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    tags=["Inspection"],
)
async def inspect_image(file: UploadFile = File(...)):
    # 1. Validation du nom / extension avant toute lecture couteuse
    validate_extension(file.filename)

    # 2. Lecture en flux avec coupure anticipee si le fichier est trop lourd
    content = await read_upload_within_limit(file, settings.MAX_IMAGE_SIZE)

    # 3. Verification du format reel (magic bytes), independamment de l'extension
    validate_magic_bytes(content)

    # 4. Inference
    if vision_service is None:
        return JSONResponse(status_code=503, content={"error": "Modele non initialise."})

    try:
        result = vision_service.predict(content)
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:  # garde-fou : ne jamais laisser un plantage remonter brut au client
        logger.exception("Erreur inattendue pendant l'inference")
        return JSONResponse(status_code=500, content={"error": f"Erreur interne pendant l'analyse : {exc}"})

    result.update(
        {
            "filename": file.filename,
            "file_size": len(content),
            "timestamp": datetime.now().isoformat(),
        }
    )
    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

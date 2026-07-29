"""
Validation et lecture securisee du fichier uploade.
Objectif du sujet : "bloquer les fichiers non-images ou trop lourds
pour eviter les plantages" et "ne pas saturer la memoire du serveur".
"""
import os

from fastapi import UploadFile, HTTPException

from app.config import settings

# Signatures binaires (magic bytes) des formats d'image acceptes.
# On ne fait jamais confiance a l'extension seule : un fichier .jpg
# peut contenir n'importe quoi.
IMAGE_SIGNATURES = {
    b"\xff\xd8\xff": "JPEG",
    b"\x89PNG\r\n\x1a\n": "PNG",
    b"RIFF": "WEBP",   # RIFF....WEBP, verifie plus finement ci-dessous
    b"BM": "BMP",
}


def validate_extension(filename: str) -> None:
    """Rejette immediatement les extensions non supportees, avant toute lecture."""
    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Extension non supportee : '{ext}'. Extensions autorisees : {sorted(settings.ALLOWED_EXTENSIONS)}",
        )


def validate_magic_bytes(content: bytes) -> None:
    """Verifie que le contenu binaire correspond bien a une image, pas seulement le nom du fichier."""
    if content.startswith(b"RIFF") and b"WEBP" not in content[:16]:
        raise HTTPException(status_code=400, detail="Le fichier n'est pas une image valide.")

    if not any(content.startswith(sig) for sig in IMAGE_SIGNATURES):
        raise HTTPException(status_code=400, detail="Le fichier n'est pas une image valide.")


async def read_upload_within_limit(file: UploadFile, max_size: int) -> bytes:
    """
    Lit le fichier par blocs de 1 Mo au lieu d'un seul `file.read()`.

    Ainsi, si un client envoie un fichier de plusieurs Go, la lecture est
    interrompue des que la limite est depassee : on ne charge jamais
    l'integralite d'un fichier surdimensionne en memoire avant de le rejeter.
    """
    chunk_size = 1024 * 1024
    buffer = bytearray()

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        buffer.extend(chunk)
        if len(buffer) > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"Image trop volumineuse (max {max_size} octets).",
            )

    if len(buffer) == 0:
        raise HTTPException(status_code=400, detail="Fichier vide.")

    return bytes(buffer)

"""
Service d'inference vision par ordinateur.

Choix d'architecture : classification "zero-shot" avec CLIP .

Pourquoi : un classifieur ImageNet reconnait des OBJETS ("pull", "chaise",
"bouteille"), pas des ANOMALIES. Il n'existe pas de classe "troue" ou
"raye" dans ImageNet, donc ce type de modele ne peut structurellement pas
repondre au besoin metier sans etre re-entraine sur un jeu d'images
"conforme" / "defaut" - jeu de donnees que l'atelier ne fournit pas.

CLIP resout ce probleme sans donnees d'entrainement : on compare l'image
a des DESCRIPTIONS TEXTUELLES ("produit en parfait etat" vs "produit
endommage, raye, fissure...") et on regarde laquelle est la plus proche
semantiquement. C'est directement exploitable des le depart.

Voir README.md pour la comparaison avec le second modele candidat.
"""
import io
import logging

import torch
from PIL import Image, UnidentifiedImageError
from transformers import CLIPModel, CLIPProcessor

logger = logging.getLogger("vision_service")

CONFORME_PROMPTS = [
    "defect-free industrial surface",
    "clean smooth metal surface",
    "uniform manufactured surface",
    "perfect industrial part",
    "acceptable industrial part",
    "passed quality inspection",
    "accepted quality inspection",
    "no visible surface defects",
    "a close-up photo of a conforming industrial product with a smooth, uniform and defect-free surface",
    "a manufactured industrial part accepted after visual quality inspection, with no scratches, cracks, corrosion or contamination",
    "a high-quality metal or plastic industrial component with a clean finish, uniform texture and no visible defects",
    "an industrial product with excellent surface quality, free of dents, stains, pits, oxidation and manufacturing flaws",
    "a production line part meeting quality standards, showing a flawless and homogeneous surface",
    "a visually perfect industrial component with consistent color, texture and finish across the entire surface"
]

DEFAUT_PROMPTS = [
    "defective industrial surface",
    "corroded surface",
    "scratched surface",
    "cracked surface",
    "damaged metal surface",
    "damaged industrial part",
    "corroded industrial part",
    "failed quality inspection",
    "rejected quality inspection",
    "visible surface defects",
    "a close-up photo of a defective industrial product with visible surface defects",
    "a manufactured industrial part rejected during visual quality inspection because of scratches, cracks, corrosion or contamination",
    "a metal or plastic industrial component with damaged finish, rough texture, dents or manufacturing defects",
    "an industrial product showing corrosion, oxidation, pitting, stains, chipped areas or surface irregularities",
    "a production line part failing quality inspection due to visible surface damage or poor finishing",
    "a defective industrial component with obvious imperfections affecting surface quality"
]

ALL_PROMPTS = CONFORME_PROMPTS + DEFAUT_PROMPTS
N_CONFORME = len(CONFORME_PROMPTS)


class VisionService:
    """Encapsule le chargement du modele et la logique d'inference (separation des responsabilites)."""

    def __init__(self, model_name: str, device: str = "cpu"):
        self.device = device
        logger.info("Chargement du modele %s sur %s ...", model_name, device)
        self.model = CLIPModel.from_pretrained(model_name).to(device)
        self.model.eval()
        self.processor = CLIPProcessor.from_pretrained(model_name)
        logger.info("Modele charge.")

    @torch.inference_mode()
    def predict(self, image_bytes: bytes) -> dict:
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        except UnidentifiedImageError as exc:
            raise ValueError("Impossible de decoder l'image (fichier corrompu ou format invalide).") from exc

        inputs = self.processor(
            text=ALL_PROMPTS,
            images=image,
            return_tensors="pt",
            padding=True,
        ).to(self.device)

        outputs = self.model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=-1)[0]

        score_conforme = probs[:N_CONFORME].sum().item()
        score_defaut = probs[N_CONFORME:].sum().item()

        best_idx = int(probs.argmax().item())
        best_prompt = ALL_PROMPTS[best_idx]

        status = "conforme" if score_conforme >= score_defaut else "defaut"
        confidence = max(score_conforme, score_defaut)

        return {
            "status": status,
            "confidence": round(confidence, 4),
            "label_detail": best_prompt,
        }

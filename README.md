# Contrôle Qualité Automatisé des Produits

Micro-service de vision par ordinateur développé avec **FastAPI** permettant d'automatiser le contrôle qualité de produits manufacturés ou artisanaux.

L'API reçoit une image d'un produit et détermine automatiquement si celui-ci est :

- ✅ Conforme
- ❌ Défaut

La classification est réalisée grâce à un modèle **OpenCLIP** du Hub Hugging Face en mode **Zero-Shot**.

---

# Fonctionnalités

- Inspection automatique d'une image
- Classification : Conforme / Défaut
- Retour d'un score de confiance
- Validation du type de fichier
- Limitation de la taille des images
- Gestion des erreurs

---

# Technologies

- Python 3.12
- FastAPI
- Uvicorn
- PyTorch
- Hugging Face Transformers
- Pillow

---

# Modèle utilisé

**Nom du modèle**

```
laion/CLIP-ViT-H-14-laion2B-s32B-b79K
```

Le modèle compare l'image reçue à plusieurs descriptions textuelles représentant les classes **Conforme** et **Défaut** afin de déterminer la catégorie la plus probable.

---

# Structure du projet

```
.
├── app
│   ├── config.py           # Configuration et variables d'environnement
│   ├── main.py             # Point d'entrée FastAPI
│   ├── schemas.py          # Schémas Pydantic
│   ├── validators.py       # Validation des fichiers images
│   └── vision_service.py   # Chargement du modèle et prédiction
├── README.md
└── requirements.txt
```

---

# Installation

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Créer le fichier `.env` à partir du modèle :

```bash
cp .env.example .env
```

Modifier les variables si nécessaire.

Exemple :

```env
MODEL_NAME=laion/CLIP-ViT-H-14-laion2B-s32B-b79K
DEVICE=cpu
MAX_IMAGE_SIZE=5242880
DEFECT_CONFIDENCE_THRESHOLD=0.60
```

---

# Lancer le serveur

```bash
uvicorn app.main:app --reload --port 8000
```

Une fois lancé :

```
http://localhost:8000/docs
```

permet d'accéder à la documentation Swagger.

---

# Endpoint

## POST /inspect-image

Analyse une image envoyée au format **multipart/form-data**.

### Paramètre

| Nom | Type |
|------|------|
| image | File |

### Réponse

Produit conforme :

```json
{
    "status": "conforme",
    "confidence": 0.95
}
```

Produit présentant un défaut :

```json
{
    "status": "defaut",
    "confidence": 0.91
}
```

---

# Sécurité

Le micro-service vérifie :

- que le fichier envoyé est bien une image ;
- que la taille maximale autorisée n'est pas dépassée ;
- les erreurs lors de la lecture de l'image ;
- les exceptions liées au chargement ou à l'inférence du modèle.

---

# Principe de fonctionnement

1. Le client envoie une image.
2. Le fichier est validé.
3. L'image est prétraitée.
4. OpenCLIP extrait les caractéristiques visuelles.
5. Les caractéristiques sont comparées aux descriptions textuelles des classes **Conforme** et **Défaut**.
6. L'API retourne la classe prédite et son niveau de confiance.

---

# Auteur

Projet réalisé dans le cadre de l'Atelier 35 – Contrôle Qualité Automatisé des Produits sur une Ligne de Production.
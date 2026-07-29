# Évaluation des modèles de Vision

## Contexte

L'objectif est de sélectionner un modèle de vision capable de classifier automatiquement une image de produit en :

- Conforme
- Défaut

Les critères étudiés sont :

- précision
- taille du modèle
- performances CPU
- licence
- facilité d'intégration avec Hugging Face

---

# Modèle candidat n°1

## Nom

OpenAI CLIP ViT-B/32

## Hub

https://huggingface.co/openai/clip-vit-base-patch32

## Architecture

Vision Transformer (ViT-B/32)

## Taille

≈ 600 MB

## Licence

MIT

## Avantages

- modèle léger
- très populaire
- rapide sur CPU
- facilement intégrable avec Transformers

## Inconvénients

- moins performant sur les détails fins
- précision limitée pour des défauts industriels subtils (rayures, corrosion, texture)

---

# Modèle candidat n°2 (choisi)

## Nom

OpenCLIP ViT-H/14

## Hub

https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K

## Architecture

Vision Transformer H/14

## Taille

≈ 4 Go

## Licence

MIT

## Avantages

- meilleures représentations visuelles
- meilleure compréhension des textures
- meilleure détection des défauts de surface
- très bonnes performances en Zero-Shot
- compatible avec Hugging Face

## Inconvénients

- plus lent sur CPU
- mémoire plus importante

---

# Comparaison

| Critère | CLIP ViT-B/32 | OpenCLIP ViT-H/14 |
|----------|---------------|-------------------|
| Architecture | ViT-B/32 | ViT-H/14 |
| Taille | ≈ 600 MB | ≈ 4 Go |
| Licence | MIT | MIT |
| CPU | Très rapide | Plus lent |
| Qualité des représentations | Bonne | Excellente |
| Détection des textures | Moyenne | Très bonne |
| Adapté au Zero-Shot | Oui | Oui |

---

# Choix final

Le modèle **OpenCLIP ViT-H/14** a été retenu.

Ce modèle offre de meilleures performances pour la classification Zero-Shot d'images industrielles grâce à des représentations visuelles plus riches. Malgré une taille plus importante et un temps d'inférence supérieur sur CPU, il fournit des résultats plus fiables pour distinguer un produit conforme d'un produit présentant des défauts de surface (rayures, corrosion, fissures, mauvaise finition).

Son utilisation répond également aux contraintes du projet :

- intégration simple avec Hugging Face ;
- licence MIT compatible avec un usage commercial ;
- fonctionnement sur CPU ;
- bonne robustesse pour un micro-service FastAPI.
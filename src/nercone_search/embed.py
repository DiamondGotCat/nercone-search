# ┌─────────────────────────────────────────┐
# │ embed.py on Nercone Search              │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import torch
from .config import EmbeddingModel
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(EmbeddingModel)

def embed(text: str) -> torch.Tensor:
    return model.encode(text, normalize_embeddings=True)

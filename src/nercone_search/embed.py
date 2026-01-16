# ┌─────────────────────────────────────────┐
# │ embed.py on Nercone Search              │
# │ Copyright (c) 2026 DiamondGotCat        │
# │ Made by Nercone / MIT License           │
# └─────────────────────────────────────────┘

import torch
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from .config import config

model = SentenceTransformer(config.get("EmbeddingModel"))

@lru_cache(maxsize=config.get("EmbeddingCacheSize"))
def embed(text: str) -> torch.Tensor:
    return model.encode(text, normalize_embeddings=True)

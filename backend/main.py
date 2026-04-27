"""
Géni_Electrique — API Backend
==============================
FastAPI + SQLAlchemy + sentence-transformers

Démarrage local :
  uvicorn main:app --reload --port 8000

Endpoints principaux :
  GET  /api/articles/           → liste catalogue
  POST /api/articles/           → créer un article
  POST /api/articles/search     → matching sémantique ★
  POST /api/articles/reindex    → (re)vectoriser le catalogue
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine, Base
from routers import articles
from embeddings.engine import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pré-charger le modèle au démarrage (évite le cold-start à la 1ère requête)
    get_model()
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Géni_Electrique API",
    version="1.0.0",
    description="Moteur de matching sémantique pour articles électriques",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)


@app.get("/")
def root():
    return {
        "projet": "Géni_Electrique",
        "version": "1.0.0",
        "moteur": "sentence-transformers / paraphrase-multilingual-MiniLM-L12-v2",
        "status": "ok",
    }

"""
Router : Articles & Matching sémantique
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from models.article import Article
from embeddings.engine import search, embed_articles, encode

router = APIRouter(prefix="/api/articles", tags=["Articles"])


# ── Schémas ───────────────────────────────────────────────────────────────────

class ArticleCreate(BaseModel):
    reference:      str
    designation:    str
    marque:         Optional[str] = None
    categorie:      Optional[str] = None
    sous_categorie: Optional[str] = None
    unite:          str = "U"
    prix_unitaire:  float = 0.0
    description:    Optional[str] = None


class ArticleOut(BaseModel):
    id:             int
    reference:      str
    designation:    str
    marque:         Optional[str]
    categorie:      Optional[str]
    sous_categorie: Optional[str]
    unite:          str
    prix_unitaire:  float
    has_embedding:  bool

    model_config = {"from_attributes": True}


class MatchResult(BaseModel):
    id:             int
    reference:      str
    designation:    str
    categorie:      str
    marque:         str
    prix_unitaire:  float
    unite:          str
    score:          float
    score_pct:      int
    match_type:     str


class SearchRequest(BaseModel):
    designation: str
    top_k:       int = 8
    seuil:       float = 0.45
    hybrid:      bool = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[ArticleOut])
def list_articles(
    q:         Optional[str] = Query(None, description="Filtre texte libre"),
    categorie: Optional[str] = Query(None),
    limit:     int = Query(50, le=500),
    db: Session = Depends(get_db),
):
    """Liste les articles du catalogue avec filtre optionnel."""
    query = db.query(Article)
    if q:
        query = query.filter(Article.designation.ilike(f"%{q}%"))
    if categorie:
        query = query.filter(Article.categorie == categorie)
    return query.order_by(Article.designation).limit(limit).all()


@router.post("/", response_model=ArticleOut, status_code=201)
def create_article(payload: ArticleCreate, db: Session = Depends(get_db)):
    """Crée un article et calcule immédiatement son embedding."""
    if db.query(Article).filter(Article.reference == payload.reference).first():
        raise HTTPException(400, f"Référence '{payload.reference}' déjà existante")

    art = Article(**payload.model_dump())
    # Calcul embedding au moment de la création
    texte = " ".join(filter(None, [
        art.designation, art.categorie, art.sous_categorie, art.marque
    ]))
    art.embedding = encode(texte)
    db.add(art)
    db.commit()
    db.refresh(art)
    art.has_embedding = art.embedding is not None
    return art


@router.post("/search", response_model=list[MatchResult])
def semantic_search(payload: SearchRequest, db: Session = Depends(get_db)):
    """
    Recherche sémantique — cœur du moteur de matching.
    Encode la désignation et retourne les articles les plus proches
    par similarité cosinus sur les embeddings sentence-transformers.
    """
    if not payload.designation.strip():
        raise HTTPException(400, "Désignation vide")

    results = search(
        designation=payload.designation,
        db=db,
        top_k=payload.top_k,
        seuil=payload.seuil,
        hybrid=payload.hybrid,
    )
    return results


@router.post("/reindex", status_code=202)
def reindex_embeddings(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Lance la (re)vectorisation de tous les articles sans embedding.
    Tâche en arrière-plan — retourne immédiatement.
    """
    background_tasks.add_task(embed_articles, db)
    return {"message": "Vectorisation lancée en arrière-plan."}


@router.get("/{article_id}", response_model=ArticleOut)
def get_article(article_id: int, db: Session = Depends(get_db)):
    art = db.query(Article).filter(Article.id == article_id).first()
    if not art:
        raise HTTPException(404, "Article introuvable")
    art.has_embedding = art.embedding is not None
    return art

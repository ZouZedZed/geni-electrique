"""
Moteur de matching sémantique — sentence-transformers
=====================================================
Modèle : paraphrase-multilingual-MiniLM-L12-v2
  → multilingue (français inclus), léger (~120 MB), 384 dimensions
  → comprend les synonymes : "câble" ↔ "fil", "disjoncteur" ↔ "coupe-circuit"

Workflow :
  1. embed_articles()  — à lancer une fois (ou après chaque import catalogue)
     génère et stocke les vecteurs en base de données
  2. search()          — à chaque requête utilisateur
     encode la désignation + calcule la similarité cosinus avec tous les vecteurs BDD
     retourne les N meilleurs résultats avec leur score
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from models.article import Article

# Chargement unique du modèle (au démarrage de l'application)
_model: SentenceTransformer | None = None

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def get_model() -> SentenceTransformer:
    """Charge le modèle en mémoire une seule fois (singleton)."""
    global _model
    if _model is None:
        print(f"[Embeddings] Chargement du modèle {MODEL_NAME}…")
        _model = SentenceTransformer(MODEL_NAME)
        print("[Embeddings] Modèle prêt.")
    return _model


def encode(text: str) -> list[float]:
    """Encode un texte en vecteur 384 dimensions."""
    model = get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Similarité cosinus entre deux vecteurs déjà normalisés.
    Résultat entre 0.0 (aucun rapport) et 1.0 (identiques).
    """
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    return float(np.dot(va, vb))


def embed_articles(db: Session, batch_size: int = 64) -> int:
    """
    Calcule et stocke les embeddings de tous les articles sans vecteur.
    À appeler après un import catalogue ou une mise à jour de désignations.
    Retourne le nombre d'articles mis à jour.
    """
    model = get_model()
    articles = db.query(Article).filter(Article.embedding == None).all()

    if not articles:
        print("[Embeddings] Tous les articles sont déjà vectorisés.")
        return 0

    print(f"[Embeddings] Vectorisation de {len(articles)} articles…")
    updated = 0

    for i in range(0, len(articles), batch_size):
        batch = articles[i : i + batch_size]
        # Texte enrichi : désignation + catégorie + marque pour meilleure précision
        texts = [
            " ".join(filter(None, [
                art.designation,
                art.categorie,
                art.sous_categorie,
                art.marque,
            ]))
            for art in batch
        ]
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        for art, vec in zip(batch, vectors):
            art.embedding = vec.tolist()
            updated += 1

    db.commit()
    print(f"[Embeddings] {updated} articles vectorisés.")
    return updated


def search(
    designation: str,
    db: Session,
    top_k: int = 10,
    seuil: float = 0.45,
    hybrid: bool = True,
) -> list[dict]:
    """
    Recherche sémantique d'articles correspondant à une désignation.

    Paramètres :
      designation — texte libre issu du devis
      top_k       — nombre max de résultats à retourner
      seuil       — score minimum de similarité (0.0–1.0) — défaut 0.45
      hybrid      — si True, booste les articles dont les mots clés matchent
                    aussi littéralement (approche hybride)

    Retourne une liste de dicts triés par score décroissant :
      { id, reference, designation, categorie, marque, prix_unitaire,
        score, score_pct, match_type }
    """
    # 1. Encoder la requête
    query_vec = np.array(encode(designation), dtype=np.float32)

    # 2. Charger tous les articles vectorisés
    articles = db.query(Article).filter(Article.embedding != None).all()
    if not articles:
        return []

    resultats = []
    mots_query = set(designation.lower().split())

    for art in articles:
        vec = np.array(art.embedding, dtype=np.float32)
        score_sem = float(np.dot(query_vec, vec))  # cosine (vecteurs normalisés)

        # Boost hybride : mots exacts en commun
        score_final = score_sem
        if hybrid:
            mots_art = set(art.designation.lower().split())
            overlap   = len(mots_query & mots_art)
            if overlap > 0:
                boost = min(overlap * 0.04, 0.15)  # max +15%
                score_final = min(score_sem + boost, 1.0)

        if score_final >= seuil:
            resultats.append({
                "id"            : art.id,
                "reference"     : art.reference,
                "designation"   : art.designation,
                "categorie"     : art.categorie or "",
                "sous_categorie": art.sous_categorie or "",
                "marque"        : art.marque or "",
                "prix_unitaire" : art.prix_unitaire,
                "unite"         : art.unite,
                "score"         : round(score_final, 4),
                "score_pct"     : round(score_final * 100),
                "match_type"    : "sémantique+lexical" if hybrid else "sémantique",
            })

    # 3. Trier par score décroissant, retourner top_k
    resultats.sort(key=lambda x: x["score"], reverse=True)
    return resultats[:top_k]

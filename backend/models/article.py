from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base


class Article(Base):
    """
    Article du catalogue électrique.
    Le champ `embedding` stocke le vecteur sémantique (384 dimensions)
    généré par sentence-transformers pour la recherche de similarité.
    """
    __tablename__ = "articles"

    id              = Column(Integer, primary_key=True, index=True)
    reference       = Column(String(100), unique=True, nullable=False, index=True)
    designation     = Column(String(500), nullable=False)
    marque          = Column(String(100))
    categorie       = Column(String(100))
    sous_categorie  = Column(String(100))
    unite           = Column(String(20), default="U")
    prix_unitaire   = Column(Float, default=0.0)
    description     = Column(Text)
    # Vecteur sémantique — rempli par le script embed_articles.py
    embedding       = Column(ARRAY(Float), nullable=True)
    date_creation   = Column(DateTime, server_default=func.now())
    date_maj        = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"<Article {self.reference} — {self.designation[:40]}>"

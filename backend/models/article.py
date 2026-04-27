from sqlalchemy import Column, Integer, String, Float, Text, DateTime, func
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from database import Base


class Article(Base):
    """
    Article du catalogue électrique.
    embedding : vecteur pgvector 384 dims — recherche cosinus native via <=>
    """
    __tablename__ = "articles"

    id              = Column(Integer, primary_key=True, index=True)
    reference       = Column(String(100), unique=True, nullable=False, index=True)
    designation     = Column(String(500), nullable=False)
    marque          = Column(String(100))
    categorie       = Column(String(100), index=True)
    sous_categorie  = Column(String(100))
    unite           = Column(String(20),  default="U")
    prix_unitaire   = Column(Float,       default=0.0)
    description     = Column(Text)
    embedding       = Column(Vector(384))          # pgvector natif
    date_creation   = Column(DateTime(timezone=True), server_default=func.now())
    date_maj        = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Article {self.reference} — {self.designation[:40]}>"

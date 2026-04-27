from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL manquant dans le fichier .env")

# Supabase utilise un pooler PgBouncer (port 6543, mode Transaction).
# PgBouncer ne supporte pas les prepared statements → on les désactive.
connect_args = {}
engine_kwargs = {}

if "pooler.supabase.com" in DATABASE_URL or "supabase" in DATABASE_URL.lower():
    connect_args   = {"options": "-c statement_timeout=30000"}
    engine_kwargs  = {"pool_pre_ping": True, "connect_args": connect_args}
    # Désactiver les prepared statements pour PgBouncer
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    **engine_kwargs,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

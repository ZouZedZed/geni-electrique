# Géni Electrique

## Projet
Application de matching sémantique pour articles électriques.  
Moteur : **sentence-transformers** (`paraphrase-multilingual-MiniLM-L12-v2`) + **pgvector** Supabase.

## Stack technique
- **Backend** : FastAPI + SQLAlchemy + sentence-transformers + pgvector
- **Frontend** : Vue 3 + Vite + Vuetify
- **Base de données** : Supabase (PostgreSQL + pgvector)
- **Déploiement** : À définir

## Supabase
- **Projet** : Géni Electrique
- **Project ID** : dqxzifwyxsqeevfkwalb
- **URL** : https://dqxzifwyxsqeevfkwalb.supabase.co
- **Région** : us-east-1
- **MCP** : configuré dans claude_desktop_config.json

## Base de données — Tables
- `articles` : catalogue des articles électriques avec vecteur embedding(384)
  - pgvector activé (extension `vector`)
  - Index ivfflat sur embedding pour recherche cosinus
  - Index GIN fulltext sur designation (français)

## Moteur sémantique
- Modèle : `paraphrase-multilingual-MiniLM-L12-v2` (384 dims, multilingue)
- Fichier clé : `backend/embeddings/engine.py`
  - `encode(text)` → vecteur
  - `search(designation, db)` → top-K articles par similarité cosinus
  - `embed_articles(db)` → vectorise tout le catalogue
- Approche hybride : score sémantique + boost lexical (+15% max)

## Structure projet
```
Geni_Electrique/
├── CLAUDE.md                         ← ce fichier
├── backend/
│   ├── main.py                       ← FastAPI app
│   ├── database.py                   ← SQLAlchemy + Supabase
│   ├── requirements.txt
│   ├── .env                          ← DATABASE_URL (non commité)
│   ├── models/article.py             ← Table articles + Vector(384)
│   ├── embeddings/engine.py          ← Moteur sémantique ★
│   └── routers/articles.py           ← API REST + /search
├── frontend/
│   ├── src/views/SearchView.vue      ← Interface matching
│   └── src/views/CatalogueView.vue   ← Gestion catalogue
└── start_dev.bat                     ← Lance tout en 1 clic
```

## Prochaines étapes
- [ ] Renseigner DATABASE_URL Supabase dans backend/.env
- [ ] `pip install pgvector` + lancer `uvicorn main:app --reload`
- [ ] Importer le catalogue articles (CSV ou saisie manuelle)
- [ ] Tester le matching sémantique via /docs

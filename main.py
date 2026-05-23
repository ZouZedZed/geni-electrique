"""
Agent d'analyse visuelle de schémas électriques
Utilise Qwen2.5-VL-72B via OpenRouter
"""

import os
import base64
import httpx
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Agent Génie Électrique",
    description="Analyse visuelle de plans et schémas électriques via Qwen 2.5 VL",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
MODEL              = "qwen/qwen2.5-vl-72b-instruct:free"

SYSTEM_PROMPT = """Tu es un expert en génie électrique spécialisé dans l'analyse de schémas,
plans électriques, diagrammes unifilaires, schémas de câblage et plans d'installation.
Analyse avec précision et fournis des réponses détaillées et techniques en français."""


async def call_qwen_vl(image_b64: str, mime_type: str, prompt: str) -> str:
    """Appelle Qwen 2.5 VL via OpenRouter avec une image en base64."""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API OpenRouter non configurée.")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type":      "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_b64}"},
                    },
                    {"type": "text", "text": prompt},
                ],
            },
        ],
        "max_tokens": 2048,
    }

    headers = {
        "Authorization":  f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type":   "application/json",
        "HTTP-Referer":   "https://genie-electrique.northflank.app",
        "X-Title":        "Agent Génie Électrique",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        return data["choices"][0]["message"]["content"]


# ── Endpoints ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    """Interface web de test."""
    return HTMLResponse(content=open("index.html", encoding="utf-8").read())


@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL}


@app.post("/analyze")
async def analyze(
    file:   UploadFile = File(..., description="Schéma ou plan électrique (PNG, JPG, PDF)"),
    prompt: str        = Form(default="Analyse ce schéma électrique en détail."),
):
    """
    Analyse un schéma électrique via Qwen 2.5 VL.
    - **file** : image du schéma (PNG, JPG, WEBP, GIF)
    - **prompt** : question ou instruction spécifique
    """
    allowed = {"image/png", "image/jpeg", "image/webp", "image/gif", "image/jpg"}
    mime    = file.content_type or "image/png"
    if mime not in allowed:
        raise HTTPException(status_code=400, detail=f"Format non supporté : {mime}. Utilisez PNG, JPG ou WEBP.")

    content  = await file.read()
    img_b64  = base64.b64encode(content).decode()
    analysis = await call_qwen_vl(img_b64, mime, prompt)

    return JSONResponse({
        "filename": file.filename,
        "prompt":   prompt,
        "analysis": analysis,
        "model":    MODEL,
    })


@app.post("/analyze-url")
async def analyze_url(
    image_url: str = Form(..., description="URL publique de l'image"),
    prompt:    str = Form(default="Analyse ce schéma électrique en détail."),
):
    """Analyse une image depuis une URL publique."""
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="Clé API OpenRouter non configurée.")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {"type": "text",      "text": prompt},
                ],
            },
        ],
        "max_tokens": 2048,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type":  "application/json",
        "HTTP-Referer":  "https://genie-electrique.northflank.app",
        "X-Title":       "Agent Génie Électrique",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
        analysis = data["choices"][0]["message"]["content"]

    return JSONResponse({"image_url": image_url, "prompt": prompt, "analysis": analysis, "model": MODEL})

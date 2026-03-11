"""
LexLocal – FastAPI Backend
Endpoints:
  POST /api/query        → Gemini-powered bylaw query
  GET  /api/bylaws       → list bylaws (optional ?municipality=&category=)
  WS   /ws/ga/{session}  → live GA penalty optimizer stream
"""

import os
import json
import asyncio
import random
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

from data.bylaws import BYLAWS
from ga.engine import GAConfig, Dimension, build_violation_fn, run_ga

load_dotenv()

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
_gemini_client = genai.Client(api_key=GEMINI_KEY) if GEMINI_KEY else None

app = FastAPI(title="LexLocal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _search_bylaws(query: str, municipality: str | None = None) -> list[dict]:
    """Very fast tag + keyword search over the bylaw corpus."""
    q_words = set(query.lower().split())
    scored: list[tuple[int, dict]] = []
    for b in BYLAWS:
        if municipality and b["municipality"].lower() != municipality.lower():
            continue
        tag_hits = sum(1 for t in b["tags"] if any(w in t or t in w for w in q_words))
        text_hits = sum(1 for w in q_words if w in b["text"].lower())
        title_hits = sum(1 for w in q_words if w in b["title"].lower())
        score = tag_hits * 3 + title_hits * 2 + text_hits
        if score > 0:
            scored.append((score, b))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [b for _, b in scored[:6]]


def _bylaw_context(bylaws: list[dict]) -> str:
    parts = []
    for b in bylaws:
        parts.append(
            f"[{b['municipality']} – {b['category']}] {b['title']}\n{b['text']}"
        )
    return "\n\n".join(parts)


# ── Models ────────────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str
    municipality: str | None = None


class QueryResponse(BaseModel):
    answer: str
    matched_bylaws: list[dict]
    municipality_detected: str | None


class GARequest(BaseModel):
    bylaws_matched: list[dict]
    dimensions: list[dict]    # [{name, original, min_val, max_val, unit, weight}]
    config: dict | None = None


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok"}


@app.get("/api/bylaws")
async def list_bylaws(
    municipality: str | None = Query(None),
    category: str | None = Query(None),
):
    result = BYLAWS
    if municipality:
        result = [b for b in result if b["municipality"].lower() == municipality.lower()]
    if category:
        result = [b for b in result if b["category"].lower() == category.lower()]
    return {"bylaws": result, "total": len(result)}


@app.get("/api/municipalities")
async def municipalities():
    seen = []
    for b in BYLAWS:
        if b["municipality"] not in seen:
            seen.append(b["municipality"])
    return {"municipalities": sorted(seen)}


@app.post("/api/query", response_model=QueryResponse)
async def query_bylaws(req: QueryRequest):
    matched = _search_bylaws(req.query, req.municipality)

    # Detect municipality from query if not provided
    detected = req.municipality
    if not detected:
        for m in ["Victoria", "Saanich", "Esquimalt", "Oak Bay", "Sooke", "Langford"]:
            if m.lower() in req.query.lower():
                detected = m
                break

    if not matched:
        return QueryResponse(
            answer="No specific bylaws matched your query. Try being more specific about your location or activity.",
            matched_bylaws=[],
            municipality_detected=detected,
        )

    context = _bylaw_context(matched)
    prompt = f"""You are LexLocal, an expert on Vancouver Island municipal bylaws.
A user asked: "{req.query}"

Here are the relevant bylaws:
{context}

Provide a clear, practical answer in 2-4 sentences. State what is allowed or prohibited,
mention the key constraints (times, distances, permits), and note which municipality's
bylaw applies. Be direct and use plain English. Do not fabricate bylaws."""

    if _gemini_client:
        try:
            response = _gemini_client.models.generate_content(
                model="gemini-2.0-flash", contents=prompt
            )
            answer = response.text
        except Exception:
            answer = _fallback_answer(matched)
    else:
        answer = _fallback_answer(matched)

    return QueryResponse(
        answer=answer,
        matched_bylaws=matched,
        municipality_detected=detected,
    )


def _fallback_answer(bylaws: list[dict]) -> str:
    """Plain text fallback when Gemini key is not set."""
    lines = ["Based on the relevant bylaws:"]
    for b in bylaws[:3]:
        lines.append(f"• [{b['municipality']}] {b['title']}: {b['text'][:120]}...")
    return "\n".join(lines)


# ── WebSocket GA Stream ───────────────────────────────────────────────────────

@app.websocket("/ws/ga/{session_id}")
async def ga_stream(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        req_data = json.loads(raw)

        dims = [
            Dimension(
                name=d["name"],
                original=float(d["original"]),
                min_val=float(d["min_val"]),
                max_val=float(d["max_val"]),
                unit=d.get("unit", ""),
                weight=float(d.get("weight", 1.0)),
            )
            for d in req_data["dimensions"]
        ]

        cfg_data = req_data.get("config", {}) or {}
        config = GAConfig(
            population_size=cfg_data.get("population_size", 80),
            generations=cfg_data.get("generations", 60),
            mutation_rate=cfg_data.get("mutation_rate", 0.15),
            elitism=cfg_data.get("elitism", 4),
        )

        bylaws_matched = req_data.get("bylaws_matched", [])
        violation_fn = build_violation_fn(bylaws_matched, dims)

        async for gen_data in run_ga(dims, violation_fn, config):
            # Add human-readable suggestion for best chromosome
            best = gen_data["best_chromosome"]
            suggestion = {d.name: round(best[i], 2) for i, d in enumerate(dims)}
            gen_data["suggestion"] = suggestion
            await websocket.send_text(json.dumps(gen_data))
            await asyncio.sleep(0.04)   # ~25 fps visual update rate

        # Final message
        await websocket.send_text(json.dumps({"done": True}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"error": str(e)}))
        except:
            pass

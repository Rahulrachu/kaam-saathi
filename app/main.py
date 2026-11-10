"""KaamSaathi web app (FastAPI)."""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import tools
from .agent import Agent, interview_feedback, rewrite_bullets
from .i18n import norm_lang
from .metrics import Metrics

ROOT = Path(__file__).resolve().parent.parent
app = FastAPI(title="KaamSaathi", version="0.1.0")
agent = Agent()
metrics = Metrics(os.getenv("DATABASE_URL") or None, os.getenv("METRICS_DB"))
MAX_TEXT = 12000


class Profile(BaseModel):
    education: str = ""
    age: int | None = None
    interests: str = ""
    target_role: str = ""
    resume_text: str = Field("", max_length=MAX_TEXT)


class ChatIn(BaseModel):
    message: str = Field(..., max_length=MAX_TEXT)
    history: list[dict] = []
    profile: Profile = Profile()
    lang: str = "en"
    sid: str = ""


class ResumeIn(BaseModel):
    resume_text: str = Field(..., max_length=MAX_TEXT)
    target_role: str = ""
    lang: str = "en"
    sid: str = ""


class OppIn(BaseModel):
    education: str = ""
    age: int | None = None
    interests: str = ""
    lang: str = "en"
    sid: str = ""


class RoadmapIn(BaseModel):
    target_role: str
    current_skills: str = ""
    lang: str = "en"
    sid: str = ""


class AnswerIn(BaseModel):
    role: str
    index: int = 0
    answer: str = Field(..., max_length=4000)
    lang: str = "en"
    sid: str = ""


class EventIn(BaseModel):
    kind: str
    sid: str = ""
    lang: str = "en"
    ref: str = ""


@app.get("/api/health")
def health():
    return {"ok": True, "llm": agent.llm_enabled, "model": agent.model if agent.llm_enabled else None}


@app.post("/api/chat")
def chat(body: ChatIn):
    lang = norm_lang(body.lang)
    res = agent.chat(body.message, body.history, body.profile.model_dump(), lang)
    metrics.record("chat", body.sid, lang)
    return {"reply": res.reply, "steps": res.steps, "mode": res.mode}


@app.post("/api/resume")
def resume(body: ResumeIn):
    if len(body.resume_text.strip()) < 30:
        raise HTTPException(400, "Paste your full resume text (at least a few lines).")
    lang = norm_lang(body.lang)
    out = tools.analyze_resume(body.resume_text, body.target_role, lang)
    out["ai_rewrite"] = rewrite_bullets(agent, body.resume_text, out, lang)
    metrics.record("resume_check", body.sid, lang, out["score"])
    return out


@app.post("/api/opportunities")
def opps(body: OppIn):
    lang = norm_lang(body.lang)
    metrics.record("opportunities", body.sid, lang)
    return {"items": tools.find_opportunities(body.education, body.age, body.interests, lang)}


@app.post("/api/roadmap")
def roadmap(body: RoadmapIn):
    lang = norm_lang(body.lang)
    metrics.record("roadmap", body.sid, lang)
    return tools.skill_roadmap(body.target_role, body.current_skills, lang)


@app.get("/api/interview/{role}/{index}")
def question(role: str, index: int, lang: str = "en"):
    return tools.interview_question(role, index, norm_lang(lang))


@app.post("/api/interview/answer")
def answer(body: AnswerIn):
    lang = norm_lang(body.lang)
    out = tools.evaluate_answer(body.role, body.index, body.answer, lang)
    out["ai_feedback"] = interview_feedback(agent, out["question"], body.answer, out, lang)
    metrics.record("interview_answer", body.sid, lang, out["score"])
    return out


@app.get("/api/roles")
def roles(lang: str = "en"):
    lang = norm_lang(lang)
    return [{"id": k, "title": v["title"][lang]} for k, v in tools.roles().items()]


@app.post("/api/event")
def event(body: EventIn):
    if body.kind not in {"visit", "feedback_up", "feedback_down"}:
        raise HTTPException(400, "unknown event")
    metrics.record(body.kind, body.sid, norm_lang(body.lang), ref=body.ref)
    return {"ok": True}


@app.get("/go/{opp_id}")
def go(opp_id: str, sid: str = "", lang: str = "en"):
    """Outbound link to a programme, counted so we can report how many people we sent to apply."""
    by_id = {o["id"]: o for o in tools.opportunities()}
    if opp_id not in by_id:
        raise HTTPException(404)
    metrics.record("outbound_click", sid, norm_lang(lang), ref=opp_id)
    return RedirectResponse(by_id[opp_id]["url"], status_code=302)


@app.get("/api/impact")
def impact():
    return JSONResponse(metrics.summary())


app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/impact")
def impact_page():
    return FileResponse(ROOT / "static" / "impact.html")

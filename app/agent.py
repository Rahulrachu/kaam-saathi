"""KaamSaathi agent: Gemini function-calling loop over the career tools, with a
rule-based planner as fallback so the app never stops working."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field

import httpx

from . import tools
from .i18n import LANG_NAMES, norm_lang, t

TOOL_SCHEMAS = [
    {
        "name": "analyze_resume",
        "description": "Score the user's resume (0-100) and list concrete fixes. Use when the user shares or asks about their resume.",
        "parameters": {"type": "object", "properties": {
            "resume_text": {"type": "string", "description": "Full resume text"},
            "target_role": {"type": "string", "description": "Optional role id: software-developer, web-developer, data-analyst, customer-support, software-tester"},
        }, "required": ["resume_text"]},
    },
    {
        "name": "find_opportunities",
        "description": "Find free, verified Indian government and non-profit internships, apprenticeships, job portals and courses that fit the user.",
        "parameters": {"type": "object", "properties": {
            "education": {"type": "string", "description": "Highest education, e.g. 10th, 12th/PUC, ITI, diploma, BCA, B.Tech, MCA"},
            "age": {"type": "integer"},
            "interests": {"type": "string", "description": "Skills or fields of interest, comma separated"},
        }},
    },
    {
        "name": "skill_roadmap",
        "description": "Make a week-by-week plan from the user's current skills to a target job, with free learning resources.",
        "parameters": {"type": "object", "properties": {
            "target_role": {"type": "string", "description": "Job the user wants, in their words or a role id"},
            "current_skills": {"type": "string"},
        }, "required": ["target_role"]},
    },
    {
        "name": "interview_question",
        "description": "Get mock-interview question number `index` for a role.",
        "parameters": {"type": "object", "properties": {
            "role": {"type": "string"}, "index": {"type": "integer"},
        }, "required": ["role"]},
    },
    {
        "name": "evaluate_answer",
        "description": "Score the user's answer to mock-interview question `index` for a role and give tips.",
        "parameters": {"type": "object", "properties": {
            "role": {"type": "string"}, "index": {"type": "integer"}, "answer": {"type": "string"},
        }, "required": ["role", "index", "answer"]},
    },
]

SYSTEM = """You are KaamSaathi, a warm, practical career companion for first-time job seekers in India \
(students, freshers, ITI/diploma holders, first-generation graduates). Reply ONLY in {lang_name}. \
Use simple words. Be honest: never invent jobs, companies, salaries, stipends or deadlines. \
For programmes, internships and courses use ONLY what the find_opportunities and skill_roadmap tools return, \
and include their links. Call tools whenever they help; you may call several in a row (e.g. analyse the resume, \
then build a roadmap for the gaps, then find matching programmes). Keep replies under 180 words, with short \
bullet points. End with one clear next step.
Known profile: {profile}"""


@dataclass
class AgentResult:
    reply: str
    steps: list[dict] = field(default_factory=list)
    mode: str = "rules"


def run_tool(name: str, args: dict, lang: str) -> dict | list:
    if name == "analyze_resume":
        return tools.analyze_resume(args.get("resume_text", ""), args.get("target_role", ""), lang)
    if name == "find_opportunities":
        age = args.get("age")
        try:
            age = int(age) if age not in (None, "") else None
        except (TypeError, ValueError):
            age = None
        return tools.find_opportunities(args.get("education", ""), age, args.get("interests", ""), lang)
    if name == "skill_roadmap":
        return tools.skill_roadmap(args.get("target_role", ""), args.get("current_skills", ""), lang)
    if name == "interview_question":
        return tools.interview_question(args.get("role", ""), int(args.get("index", 0) or 0), lang)
    if name == "evaluate_answer":
        return tools.evaluate_answer(args.get("role", ""), int(args.get("index", 0) or 0), args.get("answer", ""), lang)
    return {"error": f"unknown tool {name}"}


class Agent:
    def __init__(self, api_key: str | None = None, model: str | None = None, http: httpx.Client | None = None):
        self.api_key = (api_key if api_key is not None else os.getenv("GEMINI_API_KEY", "")).strip()
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
        self.http = http or httpx.Client(timeout=40)

    @property
    def llm_enabled(self) -> bool:
        return bool(self.api_key)

    def chat(self, message: str, history: list[dict] | None = None, profile: dict | None = None,
             lang: str = "en") -> AgentResult:
        lang = norm_lang(lang)
        if self.llm_enabled:
            try:
                return self._gemini(message, history or [], profile or {}, lang)
            except Exception as e:  # network, quota, malformed output -> keep helping
                res = self._rules(message, profile or {}, lang)
                res.steps.insert(0, {"tool": "llm_unavailable", "args": {}, "note": type(e).__name__})
                return res
        return self._rules(message, profile or {}, lang)

    # ---------------------------------------------------------------- Gemini
    def _gemini(self, message: str, history: list[dict], profile: dict, lang: str) -> AgentResult:
        prof = {k: v for k, v in profile.items() if v and k != "resume_text"}
        if profile.get("resume_text"):
            prof["resume_on_file"] = "yes (pass it to analyze_resume when needed)"
        contents = [{"role": "model" if h.get("role") == "assistant" else "user", "parts": [{"text": h["content"]}]}
                    for h in history[-8:] if (h.get("content") or "").strip()]
        user_text = message
        if profile.get("resume_text") and re.search(r"resume|cv|रिज़्यूमे|ರೆಸ್ಯೂಮೆ|review|check", message, re.I):
            user_text += "\n\n[My resume]\n" + profile["resume_text"][:6000]
        contents.append({"role": "user", "parts": [{"text": user_text}]})
        body = {
            "systemInstruction": {"parts": [{"text": SYSTEM.format(lang_name=LANG_NAMES[lang], profile=json.dumps(prof, ensure_ascii=False))}]},
            "contents": contents,
            "tools": [{"functionDeclarations": TOOL_SCHEMAS}],
            "generationConfig": {"temperature": 0.3},
        }
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        steps: list[dict] = []
        for _ in range(5):
            resp = self.http.post(url, json=body, headers={"x-goog-api-key": self.api_key})
            if resp.status_code >= 400:
                raise RuntimeError(f"Gemini HTTP {resp.status_code}")
            cand = (resp.json().get("candidates") or [{}])[0] or {}
            parts = (cand.get("content") or {}).get("parts") or []
            calls = [p["functionCall"] for p in parts if "functionCall" in p]
            text = " ".join(p.get("text", "") for p in parts if p.get("text") and not p.get("thought")).strip()
            if not calls:
                if not text:
                    raise RuntimeError("empty Gemini reply")
                return AgentResult(text, steps, "llm")
            body["contents"].append({"role": "model", "parts": parts})
            responses = []
            for c in calls:
                args = dict(c.get("args") or {})
                out = run_tool(c.get("name", ""), args, lang)
                shown = {k: (v[:60] + "…" if isinstance(v, str) and len(v) > 60 else v) for k, v in args.items()}
                steps.append({"tool": c.get("name"), "args": shown, "result": out})
                responses.append({"functionResponse": {"name": c.get("name"), "response": {"result": out}}})
            body["contents"].append({"role": "user", "parts": responses})
        raise RuntimeError("too many tool rounds")

    # ---------------------------------------------------------------- rules
    def _rules(self, message: str, profile: dict, lang: str) -> AgentResult:
        low = (message or "").lower()
        steps: list[dict] = []
        out: list[str] = []
        resume = profile.get("resume_text") or (message if len(message) > 400 else "")
        role = tools.match_role(message) or tools.match_role(profile.get("target_role", "")) or ""

        if resume and (len(message) > 400 or re.search(r"resume|cv|रिज़्यूमे|ರೆಸ್ಯೂಮೆ", low)):
            r = run_tool("analyze_resume", {"resume_text": resume, "target_role": role}, lang)
            steps.append({"tool": "analyze_resume", "args": {"target_role": role}, "result": r})
            out.append(f"Resume score: {r['score']}/100")
            out += [f"• {f}" for f in r["fixes"][:6]]
        if re.search(r"intern|apprentic|job|course|scheme|naukri|नौकरी|इंटर्न|ಉದ್ಯೋಗ|ಕೆಲಸ|ಇಂಟರ್ನ್|free|programme|program", low):
            args = {"education": profile.get("education", "") or message, "age": profile.get("age"),
                    "interests": f"{profile.get('interests', '')} {message}"}
            r = run_tool("find_opportunities", args, lang)
            steps.append({"tool": "find_opportunities", "args": {k: v for k, v in args.items() if k != "interests"}, "result": r})
            out.append(t("opps_intro", lang))
            out += [f"• {o['name']}: {o['summary']} {o['url']}" for o in r]
        if role and re.search(r"roadmap|become|learn|plan|want to be|बनना|सीख|ಆಗಬೇಕು|ಕಲಿ|how to", low):
            r = run_tool("skill_roadmap", {"target_role": role, "current_skills": f"{profile.get('interests', '')} {resume}"}, lang)
            steps.append({"tool": "skill_roadmap", "args": {"target_role": role}, "result": r})
            out.append(t("roadmap_intro", lang, role=r["role"]))
            out += [f"• {s}" for s in r["steps"]]
            out += [f"• {x['name']}: {x['url']}" for x in r["resources"]]
        if not out:
            out.append(t("fallback_help", lang))
        return AgentResult("\n".join(out), steps, "rules")


def _plain_gemini(agent: "Agent", prompt: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{agent.model}:generateContent"
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.4}}
    resp = agent.http.post(url, json=body, headers={"x-goog-api-key": agent.api_key})
    if resp.status_code >= 400:
        raise RuntimeError(f"Gemini HTTP {resp.status_code}")
    parts = (((resp.json().get("candidates") or [{}])[0] or {}).get("content") or {}).get("parts") or []
    return " ".join(p.get("text", "") for p in parts if p.get("text") and not p.get("thought")).strip()


def rewrite_bullets(agent: "Agent", resume_text: str, analysis: dict, lang: str) -> str:
    """LLM rewrite of the weakest resume lines. Empty string when no LLM or on failure."""
    if not agent.llm_enabled or not resume_text.strip():
        return ""
    prompt = (
        f"You are a resume coach for Indian freshers. Reply in {LANG_NAMES[norm_lang(lang)]}.\n"
        "Pick the 3 weakest lines in this resume and rewrite each as one strong bullet "
        "(action verb + what + measurable result). Never invent facts or numbers: where a number is "
        "needed but unknown, write a placeholder like [X users]. Format: 'Before: ...' / 'After: ...'.\n"
        f"Rule-based findings: {json.dumps(analysis['fixes'], ensure_ascii=False)}\n\nRESUME:\n{resume_text[:6000]}"
    )
    try:
        return _plain_gemini(agent, prompt)
    except Exception:
        return ""


def interview_feedback(agent: "Agent", question: str, answer: str, rule_result: dict, lang: str) -> str:
    if not agent.llm_enabled or not answer.strip():
        return ""
    prompt = (
        f"You are a friendly interviewer coaching an Indian fresher. Reply in {LANG_NAMES[norm_lang(lang)]}, "
        "in at most 90 words: one thing they did well, one thing to improve, then a model answer of 3-4 sentences "
        "that a fresher could honestly say (no invented achievements).\n"
        f"Question: {question}\nAnswer: {answer[:2000]}\nChecklist result: {json.dumps(rule_result['missing'])}"
    )
    try:
        return _plain_gemini(agent, prompt)
    except Exception:
        return ""

"""Deterministic career tools. The agent (LLM) calls these; they also run on their own
when no LLM is configured, so every feature works offline and is testable."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from .i18n import SECTION_NAMES, norm_lang, t

DATA = Path(__file__).resolve().parent.parent / "data"


@lru_cache
def opportunities() -> list[dict]:
    return json.loads((DATA / "opportunities.json").read_text(encoding="utf-8"))


@lru_cache
def roles() -> dict:
    return json.loads((DATA / "roles.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- resume
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"(?:\+?91[\s-]?)?[6-9]\d{4}[\s-]?\d{5}\b")
LINK_RE = re.compile(r"(github\.com|linkedin\.com|gitlab\.com|behance\.net|kaggle\.com)", re.I)
SECTION_PATTERNS = {
    "education": r"\b(education|academic|qualification)s?\b",
    "skills": r"\b(skills?|technical skills|technologies|tools)\b",
    "projects": r"\b(projects?|portfolio)\b",
    "experience": r"\b(experience|internships?|work history|employment)\b",
}
ACTION_VERBS = {
    "built", "developed", "designed", "created", "led", "improved", "implemented", "reduced",
    "increased", "automated", "launched", "analysed", "analyzed", "organised", "organized",
    "managed", "deployed", "trained", "optimised", "optimized", "won", "delivered", "wrote",
    "taught", "solved", "migrated", "integrated", "tested", "coordinated", "mentored",
}
WEAK_PHRASES = [
    "responsible for", "hardworking", "hard working", "team player", "quick learner",
    "go-getter", "duties included", "worked on various", "self-motivated",
]


def _lines(text: str) -> list[str]:
    return [ln.strip(" \t•*-–·") for ln in text.splitlines() if ln.strip(" \t•*-–·")]


def detect_skills(text: str) -> list[str]:
    """All role-skill keywords that appear in the text (lower-case, deduplicated)."""
    low = " " + text.lower() + " "
    found = set()
    for role in roles().values():
        for words in role["skills"].values():
            for w in words:
                if re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", low):
                    found.add(w)
    return sorted(found)


def skill_gaps(text_or_skills: str, role_id: str) -> tuple[list[str], list[str]]:
    """(skills the person shows, skills missing) for a role."""
    role = roles().get(role_id)
    if not role:
        return [], []
    low = " " + text_or_skills.lower() + " "
    have, miss = [], []
    for name, words in role["skills"].items():
        hit = any(re.search(r"(?<![a-z0-9])" + re.escape(w) + r"(?![a-z0-9])", low) for w in words)
        (have if hit else miss).append(name)
    return have, miss


def analyze_resume(resume_text: str, target_role: str = "", lang: str = "en") -> dict:
    """Score a resume 0-100 with a breakdown and concrete fixes."""
    lang = norm_lang(lang)
    text = resume_text or ""
    lines = _lines(text)
    words = len(re.findall(r"\w+", text))
    low = text.lower()

    contact = {
        "email": bool(EMAIL_RE.search(text)),
        "phone": bool(PHONE_RE.search(text)),
        "links": bool(LINK_RE.search(text)),
    }
    sections = {k: bool(re.search(p, low)) for k, p in SECTION_PATTERNS.items()}
    bullet_lines = [ln for ln in lines if len(ln.split()) >= 4]
    numbered = [ln for ln in bullet_lines if re.search(r"\d", ln)
                and not EMAIL_RE.search(ln) and not PHONE_RE.search(ln)
                and not re.search(r"\b(cgpa|gpa|percentage|20\d\d)\b", ln.lower())]
    verb_lines = [ln for ln in bullet_lines if ln.split()[0].lower().strip(",.:") in ACTION_VERBS]
    weak = [p for p in WEAK_PHRASES if p in low]

    # scoring (100): contact 15, sections 30, impact numbers 20, action verbs 15, length 10, clarity 10
    score = {
        "contact": 5 * sum(contact.values()),
        "sections": int(7.5 * sum(sections.values())),
        "impact": min(20, 5 * len(numbered)),
        "action_verbs": min(15, 3 * len(verb_lines)),
        "length": 10 if 250 <= words <= 800 else (5 if 120 <= words < 250 or 800 < words <= 1100 else 0),
        "clarity": max(0, 10 - 3 * len(weak)),
    }
    total = sum(score.values())

    fixes = []
    if not contact["email"]:
        fixes.append(t("no_email", lang))
    if not contact["phone"]:
        fixes.append(t("no_phone", lang))
    if not contact["links"]:
        fixes.append(t("no_links", lang))
    for k, ok in sections.items():
        if not ok:
            fixes.append(t("missing_section", lang, section=SECTION_NAMES[k][lang]))
    if len(numbered) < 3:
        fixes.append(t("no_numbers", lang, n=len(numbered)))
    if len(verb_lines) < 3:
        fixes.append(t("few_verbs", lang))
    if weak:
        fixes.append(t("weak_phrases", lang, phrases=", ".join(f'"{w}"' for w in weak)))
    if words < 250:
        fixes.append(t("too_short", lang, words=words))
    elif words > 800:
        fixes.append(t("too_long", lang, words=words))

    gap = None
    if target_role in roles():
        have, miss = skill_gaps(text, target_role)
        gap = {"role": target_role, "have": have, "missing": miss}
        if miss:
            fixes.append(t("skills_gap", lang, role=roles()[target_role]["title"][lang], skills=", ".join(miss)))
    if not fixes:
        fixes.append(t("good_job", lang))

    return {
        "score": total,
        "breakdown": score,
        "words": words,
        "contact": contact,
        "sections": sections,
        "lines_with_numbers": len(numbered),
        "action_verb_lines": len(verb_lines),
        "weak_phrases": weak,
        "skills_found": detect_skills(text),
        "skill_gap": gap,
        "fixes": fixes,
    }


# ---------------------------------------------------------------- opportunities
EDU_ALIASES = {
    "none": ["none", "no school", "illiterate", "below 10"],
    "10th": ["10th", "sslc", "class 10", "matric", "10"],
    "12th": ["12th", "puc", "class 12", "hsc", "intermediate", "12", "2nd puc"],
    "iti": ["iti"],
    "diploma": ["diploma", "polytechnic"],
    "graduate": ["graduate", "degree", "b.e", "be", "btech", "b.tech", "bsc", "b.sc", "bcom", "b.com",
                 "ba", "b.a", "bca", "bba", "ug"],
    "postgraduate": ["postgraduate", "pg", "mca", "mba", "m.tech", "mtech", "msc", "m.sc", "ma", "m.com"],
}


def norm_education(edu: str) -> str:
    e = (edu or "").strip().lower()
    if not e:
        return ""
    for key in ("postgraduate", "graduate", "diploma", "iti", "12th", "10th", "none"):
        for a in EDU_ALIASES[key]:
            if re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", e):
                return key
    return ""


def find_opportunities(education: str = "", age: int | None = None, interests: str = "",
                       lang: str = "en", limit: int = 5) -> list[dict]:
    """Rank the curated, verified list of free programmes for this person."""
    lang = norm_lang(lang)
    edu = norm_education(education)
    want = {w.strip().lower() for w in re.split(r"[,/;]| and ", interests or "") if w.strip()}
    want |= {w for w in detect_skills(interests or "")}
    techy = bool(want & {"it", "python", "java", "web", "data", "programming", "javascript", "sql", "ai",
                         "software", "coding", "cloud", "react", "html", "css"})
    results = []
    for o in opportunities():
        if edu and edu not in o["education"]:
            continue
        if age is not None and not (o["age_min"] <= age <= o["age_max"]):
            continue
        s = 1.0
        tags = set(o["tags"])
        s += 2 * min(2, len(tags & want))
        if techy and "it" in tags:
            s += 2
        if "any" in tags:
            s += 0.5
        if o["type"] in ("internship", "apprenticeship", "jobs"):
            s += 3  # paid work first: it changes income fastest
        results.append((s, o))
    results.sort(key=lambda x: -x[0])
    return [{
        "id": o["id"], "name": o["name"], "type": o["type"], "provider": o["provider"],
        "url": o["url"], "cost": o["cost"], "summary": o["summary"][lang],
    } for _, o in results[:limit]]


# ---------------------------------------------------------------- roadmap
def match_role(text: str) -> str:
    """Map free text ('I want to be a web developer') to a role id."""
    low = (text or "").lower()
    table = [
        ("web-developer", ["web", "frontend", "front-end", "react", "full stack", "fullstack", "website"]),
        ("data-analyst", ["data", "analyst", "excel", "power bi", "tableau", "analytics"]),
        ("software-tester", ["test", "qa", "quality"]),
        ("customer-support", ["support", "bpo", "call centre", "call center", "customer", "voice process"]),
        ("software-developer", ["software", "developer", "programmer", "coder", "sde", "engineer", "python", "java"]),
    ]
    for rid, keys in table:
        if any(k in low for k in keys):
            return rid
    return ""


def skill_roadmap(target_role: str, current_skills: str = "", lang: str = "en") -> dict:
    lang = norm_lang(lang)
    rid = target_role if target_role in roles() else match_role(target_role)
    if not rid:
        rid = "software-developer"
    role = roles()[rid]
    have, miss = skill_gaps(current_skills, rid)
    steps = []
    week = 1
    for skill in miss[:4]:
        steps.append(t("roadmap_step", lang, a=week, b=week + 1, skill=skill))
        week += 2
    steps.append(t("roadmap_last", lang))
    res_ids = role["resources"]
    by_id = {o["id"]: o for o in opportunities()}
    return {
        "role_id": rid,
        "role": role["title"][lang],
        "have": have,
        "missing": miss,
        "steps": steps,
        "resources": [{"name": by_id[r]["name"], "url": by_id[r]["url"]} for r in res_ids if r in by_id],
    }


# ---------------------------------------------------------------- interview
def interview_question(role: str, index: int = 0, lang: str = "en") -> dict:
    rid = role if role in roles() else (match_role(role) or "software-developer")
    qs = roles()[rid]["questions"]
    i = max(0, int(index)) % len(qs)
    return {"role_id": rid, "role": roles()[rid]["title"][norm_lang(lang)], "index": i,
            "total": len(qs), "question": qs[i]["q"]}


def evaluate_answer(role: str, index: int, answer: str, lang: str = "en") -> dict:
    lang = norm_lang(lang)
    q = interview_question(role, index, lang)
    points = roles()[q["role_id"]]["questions"][q["index"]]["points"]
    low = (answer or "").lower()
    words = len(re.findall(r"\w+", answer or ""))
    covered = [p for p in points if all(part in low for part in p.split())]
    missing = [p for p in points if p not in covered]
    has_example = bool(re.search(r"\b(i|we|my|our)\b.*\b(built|made|did|used|fixed|solved|handled|created|worked)\b", low))
    score = min(10, round(10 * len(covered) / max(1, len(points)) * 0.6 + (2 if words >= 40 else words / 20) + (2 if has_example else 0)))
    tips = []
    if words < 25:
        tips.append(t("answer_short", lang))
    if missing:
        tips.append(t("answer_missing", lang, points=", ".join(missing)))
    if not has_example:
        tips.append(t("answer_example", lang))
    if not tips:
        tips.append(t("answer_good", lang))
    return {**q, "score": score, "out_of": 10, "covered": covered, "missing": missing, "tips": tips, "words": words}

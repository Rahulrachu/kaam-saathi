import importlib
import os

import httpx
from fastapi.testclient import TestClient


def make_client(tmp_path):
    os.environ.pop("GEMINI_API_KEY", None)
    os.environ.pop("DATABASE_URL", None)
    os.environ["METRICS_DB"] = str(tmp_path / "m.db")
    import app.main as main
    importlib.reload(main)
    return TestClient(main.app)


def test_pages_and_health(tmp_path):
    c = make_client(tmp_path)
    assert c.get("/").status_code == 200
    assert c.get("/impact").status_code == 200
    assert c.get("/api/health").json()["llm"] is False


def test_resume_flow_and_before_after_metric(tmp_path):
    c = make_client(tmp_path)
    sid = "testsession123"
    weak = "Ravi\nHardworking team player.\nResponsible for college fest and various things in my college life."
    r1 = c.post("/api/resume", json={"resume_text": weak, "sid": sid}).json()
    better = weak + "\nravi@gmail.com 9845012345 github.com/ravi\nEducation\nBCA 2025\nSkills\nPython SQL\nProjects\nBuilt a quiz app used by 120 students\n"
    r2 = c.post("/api/resume", json={"resume_text": better, "sid": sid}).json()
    assert r2["score"] > r1["score"]
    imp = c.get("/api/impact").json()
    assert imp["people"] == 1
    assert imp["resume_improved_by"] == 1
    assert imp["avg_resume_score_gain"] == r2["score"] - r1["score"]


def test_short_resume_rejected(tmp_path):
    c = make_client(tmp_path)
    assert c.post("/api/resume", json={"resume_text": "hi"}).status_code == 400


def test_opportunities_roadmap_interview_and_redirect(tmp_path):
    c = make_client(tmp_path)
    items = c.post("/api/opportunities", json={"education": "diploma", "age": 20, "interests": "it", "lang": "kn", "sid": "abcdefgh1"}).json()["items"]
    assert items and all(i["summary"] for i in items)
    rm = c.post("/api/roadmap", json={"target_role": "web-developer", "current_skills": "html"}).json()
    assert rm["role_id"] == "web-developer"
    q = c.get("/api/interview/data-analyst/1?lang=hi").json()
    assert q["index"] == 1
    a = c.post("/api/interview/answer", json={"role": "data-analyst", "index": 1, "answer": "Median is the middle value"}).json()
    assert 0 <= a["score"] <= 10
    r = c.get("/go/ncs?sid=abcdefgh1", follow_redirects=False)
    assert r.status_code == 302 and r.headers["location"] == "https://www.ncs.gov.in/"
    assert c.get("/go/nope").status_code == 404
    assert c.get("/api/impact").json()["events"]["outbound_click"] == 1


def test_event_validation(tmp_path):
    c = make_client(tmp_path)
    assert c.post("/api/event", json={"kind": "feedback_up", "sid": "abcdefgh1"}).status_code == 200
    assert c.post("/api/event", json={"kind": "resume_check"}).status_code == 400


def test_chat_with_mocked_gemini_tool_loop(tmp_path):
    """The agent calls a tool, gets the result back, then answers."""
    from app.agent import Agent
    calls = []

    def handler(request: httpx.Request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(200, json={"candidates": [{"content": {"parts": [
                {"functionCall": {"name": "find_opportunities", "args": {"education": "BCA", "age": 22, "interests": "web"}}}]}}]})
        body = request.read().decode()
        assert "functionResponse" in body and "pminternship" in body
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "Apply to PM Internship Scheme: https://pminternship.mca.gov.in/"}]}}]})

    a = Agent(api_key="test", model="m", http=httpx.Client(transport=httpx.MockTransport(handler)))
    r = a.chat("find internships", lang="en")
    assert r.mode == "llm"
    assert r.steps[0]["tool"] == "find_opportunities"
    assert "pminternship" in r.reply


def test_chat_falls_back_when_gemini_fails():
    from app.agent import Agent
    a = Agent(api_key="test", model="m", http=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    r = a.chat("find internships for me", profile={"education": "12th"})
    assert r.mode == "rules"
    assert r.steps[0]["tool"] == "llm_unavailable"

from app import tools
from app.agent import Agent

GOOD = """Asha R
asha.r@gmail.com | +91 98450 12345 | github.com/asha-r | linkedin.com/in/asha-r
Education
B.Sc Computer Science, 2025, Mysuru University, 8.1 CGPA
Skills
Python, SQL, Git, HTML, CSS, JavaScript, React, pandas, Excel
Projects
Built a bus-timing web app in React used by 300 students of my college every day
Developed a Python script that cut library report time from 2 hours to 10 minutes
Designed a MySQL database for 1,200 books with search in under 1 second
Experience
Internship, ABC Tech, Bengaluru (Jun-Aug 2024)
Automated 3 weekly Excel reports with pandas, saving the team 4 hours a week
Tested 25 web pages and filed 40 bug reports in Jira
""" + "Additional coursework in data structures and algorithms, OOP and unit testing. " * 12

WEAK = """Ravi
Hardworking team player and quick learner.
Responsible for college fest.
"""


def test_good_resume_scores_higher_than_weak():
    g = tools.analyze_resume(GOOD, "web-developer")
    w = tools.analyze_resume(WEAK)
    assert g["score"] >= 70
    assert w["score"] < 35
    assert g["contact"] == {"email": True, "phone": True, "links": True}
    assert all(g["sections"].values())
    assert "responsible for" in w["weak_phrases"]


def test_resume_fixes_are_localised():
    w_hi = tools.analyze_resume(WEAK, lang="hi")
    w_kn = tools.analyze_resume(WEAK, lang="kn")
    assert any("ईमेल" in f for f in w_hi["fixes"])
    assert any("ಇಮೇಲ್" in f for f in w_kn["fixes"])


def test_skill_gap_for_role():
    have, miss = tools.skill_gaps("I know HTML, CSS and javascript", "web-developer")
    assert "HTML & CSS" in have and "JavaScript" in have
    assert "deployment" in miss


def test_education_normalisation():
    assert tools.norm_education("BCA") == "graduate"
    assert tools.norm_education("MCA AI&ML") == "postgraduate"
    assert tools.norm_education("2nd PUC") == "12th"
    assert tools.norm_education("ITI fitter") == "iti"
    assert tools.norm_education("SSLC") == "10th"


def test_opportunities_filter_and_rank():
    items = tools.find_opportunities("ITI", 19, "electrician")
    ids = [o["id"] for o in items]
    assert "naps" in ids
    assert "nats" not in ids  # NATS needs diploma/graduate
    tech = tools.find_opportunities("B.Tech", 22, "python, web")
    assert tech[0]["type"] in ("internship", "apprenticeship", "jobs")
    old = tools.find_opportunities("12th", 40, "")
    assert all(o["id"] not in ("pm-internship", "ddu-gky") for o in old)


def test_opportunities_have_https_urls_and_three_languages():
    for o in tools.opportunities():
        assert o["url"].startswith("https://")
        assert set(o["summary"]) == {"en", "hi", "kn"}


def test_roadmap_and_role_matching():
    assert tools.match_role("I want to become a web developer") == "web-developer"
    assert tools.match_role("BPO voice process job") == "customer-support"
    r = tools.skill_roadmap("data analyst", "excel", "kn")
    assert r["role_id"] == "data-analyst"
    assert "Excel / Google Sheets" in r["have"]
    assert r["steps"] and r["resources"]


def test_interview_scoring():
    q = tools.interview_question("software-tester", 0)
    assert "login" in q["question"].lower()
    weak = tools.evaluate_answer("software-tester", 0, "I will test it.")
    strong = tools.evaluate_answer(
        "software-tester", 0,
        "I would test valid and invalid passwords, an empty username and password, and security checks like "
        "SQL injection and account lock after five tries. In my college project I built a login form and I "
        "tested these cases myself, which found two bugs before our demo.")
    assert strong["score"] > weak["score"]
    assert strong["missing"] == []


def test_rules_agent_without_llm():
    a = Agent(api_key="")
    r = a.chat("Find free internships for me", profile={"education": "BCA", "age": 21, "interests": "python"}, lang="hi")
    assert r.mode == "rules"
    assert any(s["tool"] == "find_opportunities" for s in r.steps)
    assert "https://" in r.reply
    r2 = a.chat("hello", lang="kn")
    assert "ರೆಸ್ಯೂಮೆ" in r2.reply

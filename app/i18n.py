"""Short, hand-written strings for the rule-based engine in English, Hindi and Kannada.

The LLM writes its own replies in the chosen language; these strings keep the app
fully usable (and multilingual) when no LLM key is configured or the LLM fails.
"""

LANGS = ("en", "hi", "kn")
LANG_NAMES = {"en": "English", "hi": "Hindi (हिन्दी)", "kn": "Kannada (ಕನ್ನಡ)"}

MSG = {
    "no_email": {
        "en": "Add a professional email address at the top.",
        "hi": "सबसे ऊपर एक प्रोफ़ेशनल ईमेल पता जोड़ें।",
        "kn": "ಮೇಲ್ಭಾಗದಲ್ಲಿ ವೃತ್ತಿಪರ ಇಮೇಲ್ ವಿಳಾಸ ಸೇರಿಸಿ.",
    },
    "no_phone": {
        "en": "Add a 10-digit mobile number so recruiters can call you.",
        "hi": "10 अंकों का मोबाइल नंबर जोड़ें ताकि रिक्रूटर कॉल कर सकें।",
        "kn": "ನೇಮಕಾತಿದಾರರು ಕರೆ ಮಾಡಲು 10 ಅಂಕಿಯ ಮೊಬೈಲ್ ಸಂಖ್ಯೆ ಸೇರಿಸಿ.",
    },
    "no_links": {
        "en": "Add a GitHub or LinkedIn link: for first jobs, proof of work matters more than marks.",
        "hi": "GitHub या LinkedIn लिंक जोड़ें: पहली नौकरी में अंकों से ज़्यादा काम का सबूत मायने रखता है।",
        "kn": "GitHub ಅಥವಾ LinkedIn ಲಿಂಕ್ ಸೇರಿಸಿ: ಮೊದಲ ಉದ್ಯೋಗಕ್ಕೆ ಅಂಕಗಳಿಗಿಂತ ಕೆಲಸದ ಪುರಾವೆ ಮುಖ್ಯ.",
    },
    "missing_section": {
        "en": "Add a clear \"{section}\" section.",
        "hi": "एक साफ़ \"{section}\" सेक्शन जोड़ें।",
        "kn": "ಸ್ಪಷ್ಟವಾದ \"{section}\" ವಿಭಾಗ ಸೇರಿಸಿ.",
    },
    "no_numbers": {
        "en": "Add numbers to your points (users, %, time saved, marks, rank). Only {n} line(s) have any.",
        "hi": "अपने पॉइंट्स में संख्याएँ जोड़ें (यूज़र, %, बचा समय, रैंक)। अभी सिर्फ़ {n} लाइन में हैं।",
        "kn": "ನಿಮ್ಮ ಅಂಶಗಳಿಗೆ ಸಂಖ್ಯೆಗಳನ್ನು ಸೇರಿಸಿ (ಬಳಕೆದಾರರು, %, ಉಳಿಸಿದ ಸಮಯ, ರ್ಯಾಂಕ್). ಈಗ ಕೇವಲ {n} ಸಾಲಿನಲ್ಲಿ ಇವೆ.",
    },
    "few_verbs": {
        "en": "Start points with action verbs (Built, Designed, Led, Improved) instead of \"Responsible for\".",
        "hi": "पॉइंट्स \"Responsible for\" की जगह Built, Designed, Led, Improved जैसे एक्शन शब्दों से शुरू करें।",
        "kn": "\"Responsible for\" ಬದಲು Built, Designed, Led, Improved ಮುಂತಾದ ಕ್ರಿಯಾಪದಗಳಿಂದ ಅಂಶಗಳನ್ನು ಆರಂಭಿಸಿ.",
    },
    "weak_phrases": {
        "en": "Replace vague phrases ({phrases}) with what you actually did.",
        "hi": "धुंधले शब्द ({phrases}) हटाकर लिखें कि आपने असल में क्या किया।",
        "kn": "ಅಸ್ಪಷ್ಟ ಪದಗಳನ್ನು ({phrases}) ತೆಗೆದು ನೀವು ನಿಜವಾಗಿ ಏನು ಮಾಡಿದಿರಿ ಎಂದು ಬರೆಯಿರಿ.",
    },
    "too_short": {
        "en": "Your resume is short ({words} words). Add 2–3 projects with what you built and the result.",
        "hi": "आपका रिज़्यूमे छोटा है ({words} शब्द)। 2–3 प्रोजेक्ट जोड़ें: क्या बनाया और नतीजा क्या रहा।",
        "kn": "ನಿಮ್ಮ ರೆಸ್ಯೂಮೆ ಚಿಕ್ಕದಾಗಿದೆ ({words} ಪದಗಳು). 2–3 ಪ್ರಾಜೆಕ್ಟ್‌ಗಳನ್ನು ಸೇರಿಸಿ: ಏನು ಮಾಡಿದಿರಿ, ಫಲಿತಾಂಶ ಏನು.",
    },
    "too_long": {
        "en": "Your resume is long ({words} words). Freshers should fit on one page (about 350–600 words).",
        "hi": "आपका रिज़्यूमे लंबा है ({words} शब्द)। फ़्रेशर का रिज़्यूमे एक पेज (लगभग 350–600 शब्द) में हो।",
        "kn": "ನಿಮ್ಮ ರೆಸ್ಯೂಮೆ ಉದ್ದವಾಗಿದೆ ({words} ಪದಗಳು). ಫ್ರೆಶರ್ ರೆಸ್ಯೂಮೆ ಒಂದು ಪುಟದಲ್ಲಿರಲಿ (ಸುಮಾರು 350–600 ಪದ).",
    },
    "skills_gap": {
        "en": "For {role}, you're missing: {skills}.",
        "hi": "{role} के लिए ये स्किल नहीं दिख रहीं: {skills}।",
        "kn": "{role} ಹುದ್ದೆಗೆ ಈ ಕೌಶಲ್ಯಗಳು ಕಾಣುತ್ತಿಲ್ಲ: {skills}.",
    },
    "good_job": {
        "en": "Strong basics. Now tailor the top 3 points to each job you apply for.",
        "hi": "बुनियाद मज़बूत है। अब हर नौकरी के हिसाब से ऊपर के 3 पॉइंट बदलें।",
        "kn": "ಮೂಲಭೂತ ಅಂಶಗಳು ಚೆನ್ನಾಗಿವೆ. ಈಗ ಪ್ರತಿ ಉದ್ಯೋಗಕ್ಕೆ ತಕ್ಕಂತೆ ಮೇಲಿನ 3 ಅಂಶಗಳನ್ನು ಬದಲಿಸಿ.",
    },
    "answer_short": {
        "en": "Your answer is very short. Aim for 4–6 sentences: situation, what you did, and the result.",
        "hi": "जवाब बहुत छोटा है। 4–6 वाक्य बोलें: स्थिति, आपने क्या किया, और नतीजा।",
        "kn": "ಉತ್ತರ ತುಂಬಾ ಚಿಕ್ಕದು. 4–6 ವಾಕ್ಯ ಹೇಳಿ: ಸನ್ನಿವೇಶ, ನೀವು ಏನು ಮಾಡಿದಿರಿ, ಫಲಿತಾಂಶ.",
    },
    "answer_missing": {
        "en": "Try to also cover: {points}.",
        "hi": "इन बातों को भी शामिल करें: {points}।",
        "kn": "ಇವುಗಳನ್ನೂ ಸೇರಿಸಲು ಪ್ರಯತ್ನಿಸಿ: {points}.",
    },
    "answer_good": {
        "en": "Good answer: it covers the key points. Practise saying it in under a minute.",
        "hi": "अच्छा जवाब: मुख्य बातें आ गईं। इसे एक मिनट से कम में बोलने का अभ्यास करें।",
        "kn": "ಉತ್ತಮ ಉತ್ತರ: ಮುಖ್ಯ ಅಂಶಗಳು ಇವೆ. ಒಂದು ನಿಮಿಷದೊಳಗೆ ಹೇಳುವ ಅಭ್ಯಾಸ ಮಾಡಿ.",
    },
    "answer_example": {
        "en": "Add a real example from your project, internship or college.",
        "hi": "अपने प्रोजेक्ट, इंटर्नशिप या कॉलेज से एक असली उदाहरण जोड़ें।",
        "kn": "ನಿಮ್ಮ ಪ್ರಾಜೆಕ್ಟ್, ಇಂಟರ್ನ್‌ಶಿಪ್ ಅಥವಾ ಕಾಲೇಜಿನ ಒಂದು ನಿಜವಾದ ಉದಾಹರಣೆ ಸೇರಿಸಿ.",
    },
    "fallback_help": {
        "en": "I can: 1) check your resume (paste it), 2) find free government internships, apprenticeships and courses for you, 3) run a mock interview, 4) make a skill roadmap for a job. What would you like?",
        "hi": "मैं ये कर सकता हूँ: 1) आपका रिज़्यूमे जाँचना (पेस्ट करें), 2) आपके लिए मुफ़्त सरकारी इंटर्नशिप, अप्रेंटिसशिप और कोर्स ढूँढना, 3) मॉक इंटरव्यू, 4) किसी नौकरी के लिए स्किल रोडमैप। आप क्या चाहेंगे?",
        "kn": "ನಾನು ಇವು ಮಾಡಬಲ್ಲೆ: 1) ನಿಮ್ಮ ರೆಸ್ಯೂಮೆ ಪರಿಶೀಲನೆ (ಪೇಸ್ಟ್ ಮಾಡಿ), 2) ಉಚಿತ ಸರ್ಕಾರಿ ಇಂಟರ್ನ್‌ಶಿಪ್, ಅಪ್ರೆಂಟಿಸ್‌ಶಿಪ್, ಕೋರ್ಸ್‌ಗಳ ಹುಡುಕಾಟ, 3) ಮಾಕ್ ಇಂಟರ್ವ್ಯೂ, 4) ಉದ್ಯೋಗಕ್ಕೆ ಕೌಶಲ್ಯ ರೋಡ್‌ಮ್ಯಾಪ್. ನಿಮಗೆ ಏನು ಬೇಕು?",
    },
    "opps_intro": {
        "en": "Free programmes that match you:",
        "hi": "आपके लिए उपयुक्त मुफ़्त कार्यक्रम:",
        "kn": "ನಿಮಗೆ ಹೊಂದುವ ಉಚಿತ ಕಾರ್ಯಕ್ರಮಗಳು:",
    },
    "roadmap_intro": {
        "en": "Your roadmap to {role}:",
        "hi": "{role} बनने का आपका रोडमैप:",
        "kn": "{role} ಆಗಲು ನಿಮ್ಮ ರೋಡ್‌ಮ್ಯಾಪ್:",
    },
    "roadmap_have": {
        "en": "You already show: {skills}.",
        "hi": "आपके पास पहले से है: {skills}।",
        "kn": "ನಿಮ್ಮಲ್ಲಿ ಈಗಾಗಲೇ ಇದೆ: {skills}.",
    },
    "roadmap_step": {
        "en": "Week {a}–{b}: learn {skill} and build one small project that uses it.",
        "hi": "सप्ताह {a}–{b}: {skill} सीखें और इसका एक छोटा प्रोजेक्ट बनाएँ।",
        "kn": "ವಾರ {a}–{b}: {skill} ಕಲಿಯಿರಿ ಮತ್ತು ಅದನ್ನು ಬಳಸುವ ಒಂದು ಸಣ್ಣ ಪ್ರಾಜೆಕ್ಟ್ ಮಾಡಿ.",
    },
    "roadmap_last": {
        "en": "Then: put the projects on GitHub, update your resume, and apply through the portals below.",
        "hi": "फिर: प्रोजेक्ट GitHub पर डालें, रिज़्यूमे अपडेट करें और नीचे दिए पोर्टल से आवेदन करें।",
        "kn": "ನಂತರ: ಪ್ರಾಜೆಕ್ಟ್‌ಗಳನ್ನು GitHub ಗೆ ಹಾಕಿ, ರೆಸ್ಯೂಮೆ ನವೀಕರಿಸಿ, ಕೆಳಗಿನ ಪೋರ್ಟಲ್‌ಗಳಲ್ಲಿ ಅರ್ಜಿ ಹಾಕಿ.",
    },
    "interview_next": {
        "en": "Question {n} of {total}:",
        "hi": "प्रश्न {n} / {total}:",
        "kn": "ಪ್ರಶ್ನೆ {n} / {total}:",
    },
}

SECTION_NAMES = {
    "education": {"en": "Education", "hi": "शिक्षा (Education)", "kn": "ಶಿಕ್ಷಣ (Education)"},
    "skills": {"en": "Skills", "hi": "स्किल्स (Skills)", "kn": "ಕೌಶಲ್ಯಗಳು (Skills)"},
    "projects": {"en": "Projects", "hi": "प्रोजेक्ट्स (Projects)", "kn": "ಪ್ರಾಜೆಕ್ಟ್‌ಗಳು (Projects)"},
    "experience": {"en": "Experience / Internships", "hi": "अनुभव / इंटर्नशिप", "kn": "ಅನುಭವ / ಇಂಟರ್ನ್‌ಶಿಪ್"},
}


def t(key: str, lang: str = "en", **kw) -> str:
    lang = lang if lang in LANGS else "en"
    return MSG[key][lang].format(**kw)


def norm_lang(lang: str | None) -> str:
    return lang if lang in LANGS else "en"

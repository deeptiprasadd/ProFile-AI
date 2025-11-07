import re
import math
import collections
from typing import Dict, List, Tuple

import streamlit as st
from PyPDF2 import PdfReader
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

st.set_page_config(page_title="ATS Resume Analyzer", page_icon="📄", layout="wide")

st.markdown("""
<style>
.main-title {
    text-align: center;
    font-size: 52px;
    font-weight: 700;
    margin-top: -20px;
    color: white;
}
.sub-title {
    text-align: center;
    font-size: 28px;
    font-weight: 400;
    margin-top: -10px;
    color: #bbbbbb;
}
</style>

<h1 class="main-title">ProFile</h1>
<h2 class="sub-title">ATS Resume Analyzer</h2>
""", unsafe_allow_html=True)


# ======================================================
# PDF READER (PyPDF2) ✅ Streamlit Cloud Safe
# ======================================================
def read_uploaded_file(file) -> str:
    if not file:
        return ""
    try:
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text() or ""
            text += extracted + "\n"
        return text
    except:
        return ""


# ======================================================
# CLEAN STRUCTURED PREVIEW
# ======================================================
SECTION_TOKENS = [
    "summary", "objective", "skills", "education", "experience",
    "projects", "certifications", "leadership", "achievements"
]

def clean_preview_text(text: str) -> str:
    lines = text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        if not line:
            cleaned.append("")
            continue

        # Section headings
        if line.isupper() or any(h in line.lower() for h in SECTION_TOKENS):
            cleaned.append("\n" + line.upper())
            continue

        # Bullet cleanup
        if re.match(r"^[•\-\*]", line):
            cleaned.append("  - " + line.lstrip("•-* ").strip())
        else:
            cleaned.append(line)

    return "\n".join(cleaned)


# ======================================================
# SKILL & VERB LEXICONS
# ======================================================
ACTION_VERBS = {
    "built","designed","led","optimized","automated","deployed","shipped",
    "improved","analyzed","implemented","integrated","scaled","reduced",
    "increased","architected","launched","refactored","delivered",
    "spearheaded","orchestrated"
}

SKILL_LEXICON = {
    "Programming": {"python","java","c++","c","javascript","typescript","r","sql"},
    "Data/ML": {"pandas","numpy","matplotlib","scikit-learn","tensorflow","pytorch","keras","xgboost","nlp","computer vision"},
    "BI/Analytics": {"excel","power bi","tableau","dashboard","kpi","reporting"},
    "Web/Backend": {"flask","fastapi","django","api","rest"},
    "DevOps/MLOps": {"git","docker","kubernetes","github actions","ci/cd"},
    "Cloud/DB": {"aws","gcp","azure","mysql","postgres","snowflake","bigquery","mongodb"}
}

STOPWORDS = set((
    "a an the and or of for to with in on at as by from into over under about "
    "is are was were be being been it this that these those you your our their "
    "he she they them his her its who which what where when why how not then "
    "also using used via including include includes".split()
))


# ======================================================
# HELPER FUNCTIONS
# ======================================================
def words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z\+\#\-]{1,}", text.lower())


def extract_skills(text: str) -> Dict[str, List[str]]:
    found = {}
    low = text.lower()

    for cat, items in SKILL_LEXICON.items():
        hits = []
        for skill in items:
            if " " in skill:
                if skill in low:
                    hits.append(skill)
            else:
                if re.search(fr"\b{skill}\b", low):
                    hits.append(skill)
        if hits:
            found[cat] = sorted(set(hits))

    return found


def detect_missing_sections(text: str) -> List[str]:
    low = text.lower()
    missing = []

    if "summary" not in low:
        missing.append("Add a strong 2–3 line Professional Summary.")
    if "project" not in low:
        missing.append("Add at least 2–3 project highlights.")
    if "experience" not in low:
        missing.append("Add Experience section (internships, freelance, roles).")
    if "education" not in low:
        missing.append("Add Education details.")
    if "skill" not in low:
        missing.append("Add Skills section.")
    if not ("linkedin" in low or "github" in low):
        missing.append("Add LinkedIn / GitHub links.")

    return missing


def detect_format_issues(text: str) -> List[str]:
    issues = []
    if re.search(r"\|.+\|", text):
        issues.append("Remove table formatting — ATS cannot read tables.")
    if re.search(r"[●■◆▶▪]", text):
        issues.append("Avoid fancy bullet icons — use '-' or '*'.")
    return issues


# ======================================================
# ATS BREAKDOWN — 100-POINT SYSTEM
# ======================================================
def ats_breakdown(text: str, exp_level: str):
    fmt_issues = detect_format_issues(text)

    fmt_score = 20 - min(8, 2 * len(fmt_issues))
    skills_found = extract_skills(text)
    skills_score = min(20, len(skills_found) * 4)

    keyword_score = min(15, int(1.5 * sum(len(v) for v in skills_found.values())))

    verbs = sum(1 for v in ACTION_VERBS if v in text.lower())
    exp_score = min(20, min(10, verbs) + (5 if "experience" in text.lower() else 0))

    metrics = len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text))
    metrics_score = min(15, metrics)

    seniority_score = 10  # simple for now

    total = fmt_score + skills_score + keyword_score + exp_score + metrics_score + seniority_score
    total = min(100, max(0, total))

    breakdown = {
        "Formatting": fmt_score,
        "Skills Relevance": skills_score,
        "Keyword Coverage": keyword_score,
        "Experience Strength": exp_score,
        "Metrics & Impact": metrics_score,
        "Seniority Alignment": seniority_score
    }

    suggestions = []
    suggestions += fmt_issues
    if skills_score < 12:
        suggestions.append("Add more technical and domain-specific skills.")
    if keyword_score < 12:
        suggestions.append("Mention key tools inside experience bullets.")
    if exp_score < 12:
        suggestions.append("Add more action verbs at the start of bullets.")
    if metrics_score < 8:
        suggestions.append("Add measurable results (%, time saved, amount improved).")

    return total, breakdown, suggestions


# ======================================================
# GAUGE
# ======================================================
def draw_half_gauge(score: int):
    width, height = 600, 350
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.arc((50, 50, 550, 550), 180, 0, fill="lightgray", width=40)
    end_angle = 180 + (180 * score / 100)
    draw.arc((50, 50, 550, 550), 180, end_angle, fill="green", width=40)
    draw.text((260, 200), f"{score}%", fill="black")
    return img


# ======================================================
# LOCAL VISUAL SUGGESTION IMAGE ✅ no more broken link
# ======================================================
def generate_layout_suggestion():
    img = Image.new("RGB", (900, 350), "#f5f5f5")
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, 880, 330), fill="white")

    draw.text((40, 40), "Resume Layout Suggestions", fill="black")

    bullets = [
        "• Use sections: Summary | Skills | Experience | Projects | Education",
        "• Keep font size between 10–12",
        "• Avoid tables, shapes, icons — ATS cannot read them",
        "• Use measurable bullets (%, numbers)",
        "• Maintain equal spacing & clear hierarchy"
    ]

    y = 90
    for b in bullets:
        draw.text((40, y), b, fill="gray")
        y += 40

    return img


# ======================================================
# AI RESUME CARD PREVIEW
# ======================================================
def generate_ai_resume(text):
    img = Image.new("RGB", (950, 1300), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 910, 1260), fill="#f5f5f5")

    draw.text((60, 60), "AI-Improved Resume Layout", fill="black")

    sections = {
        "SUMMARY": text[:220] or "Add a 2–3 line summary.",
        "SKILLS": "Python • SQL • ML • Power BI",
        "EXPERIENCE": "Use action verbs + metrics.",
        "EDUCATION": "Add degree + institute + year"
    }

    y = 150
    for h, c in sections.items():
        draw.rectangle((60, y, 890, y+220), fill="white")
        draw.text((80, y+10), h, fill="black")
        draw.multiline_text((80, y+60), c, fill="gray", spacing=6)
        y += 240

    return img


# ======================================================
# AUTO TEMPLATE FILL
# ======================================================
def auto_fill_template(text):
    names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", text)
    name = names[0] if names else "FULL NAME"

    skills = re.findall(r"python|sql|excel|tableau|power bi|ml|numpy|pandas", text.lower())
    skills = ", ".join(sorted(set(skills))) or "Technical Skills Not Detected"

    return f"""
-----------------------------------------
| {name} |
-----------------------------------------

SUMMARY
Motivated candidate skilled in {skills}.

SKILLS
• {skills}

PROJECTS
• Add measurable project details here

EDUCATION
• Add degree, institute and year
"""


# ======================================================
# Recruiter View Simulation
# ======================================================
def recruiter_view(text: str):
    bullets = re.findall(r"(?:^|\n)\s*(?:•|\-|\*)\s*(.+)", text)
    metrics = re.findall(r"\b\d+(?:\.\d+)?%?\b", text)
    skills = extract_skills(text)

    top_skills = sorted(
        ((k, len(v)) for k, v in skills.items()),
        key=lambda x: -x[1]
    )[:3]

    read = []
    if len(bullets) < 6:
        read.append("Add more bullet points with action verbs.")
    if len(metrics) < 3:
        read.append("Add measurable outcomes (time saved, % improvement).")
    if "summary" not in text.lower():
        read.append("Add a professional summary at the top.")

    return {
        "top_skills": [f"{c} ({n})" for c, n in top_skills],
        "quick_reads": bullets[:5],
        "readability": read
    }


# ======================================================
# UI
# ======================================================

with st.sidebar:
    st.header("Upload Resume")
    file = st.file_uploader("Upload PDF Resume")
    exp_level = st.selectbox("Experience Level", ["Fresher","Intern","1+ Years","5+ Years"])
    btn = st.button("Analyze", type="primary")

resume = read_uploaded_file(file) if btn and file else ""

tabs = st.tabs([
    "Preview","ATS Score","Missing Sections","AI Resume",
    "Auto Sample Template","Insights","Recruiter View"
])


# ======================================================
# Preview
# ======================================================
with tabs[0]:
    if resume:
        st.text_area("Parsed Resume", clean_preview_text(resume), height=360)
    else:
        st.info("Upload a resume to begin.")


# ======================================================
# ATS Score
# ======================================================
with tabs[1]:
    if resume:
        score, breakdown, tips = ats_breakdown(resume, exp_level)
        st.image(draw_half_gauge(score))

        st.subheader("Score Breakdown")
        for k, v in breakdown.items():
            st.write(f"**{k}**: {v}")

        st.subheader("Suggestions")
        for t in tips:
            st.write("✅", t)
    else:
        st.info("Upload resume to calculate ATS score.")


# ======================================================
# Missing Sections
# ======================================================
with tabs[2]:
    if resume:
        st.subheader("Missing Sections")
        for m in detect_missing_sections(resume):
            st.write("✅", m)

        st.subheader("Visual Improvement Suggestion")
        st.image(generate_layout_suggestion())
    else:
        st.info("Upload resume.")


# ======================================================
# AI Resume
# ======================================================
with tabs[3]:
    if resume:
        st.image(generate_ai_resume(resume))
    else:
        st.info("Upload resume.")


# ======================================================
# Auto Template
# ======================================================
with tabs[4]:
    if resume:
        st.code(auto_fill_template(resume))
    else:
        st.info("Upload resume.")


# ======================================================
# Insights
# ======================================================
def plot_top_words(text):
    tokens = [w for w in words(text) if w not in STOPWORDS and len(w)>2]
    counts = collections.Counter(tokens).most_common(10)

    if not counts:
        st.info("Not enough content for insights.")
        return

    labels, vals = zip(*counts)
    fig = plt.figure(figsize=(6,3))
    plt.bar(range(len(vals)), vals)
    plt.xticks(range(len(labels)), labels, rotation=45)
    st.pyplot(fig)

with tabs[5]:
    if resume:
        st.subheader("Top Word Frequency")
        plot_top_words(resume)
    else:
        st.info("Upload resume.")


# ======================================================
# Recruiter View
# ======================================================
with tabs[6]:
    if resume:
        rv = recruiter_view(resume)

        st.subheader("Top Skills Recruiters Will Notice")
        for s in rv["top_skills"]:
            st.write("•", s)

        st.subheader("First 5 Bullets Recruiters Read")
        if rv["quick_reads"]:
            for b in rv["quick_reads"]:
                st.write("•", b)
        else:
            st.write("• No bullets detected.")

        st.subheader("Readability Suggestions")
        for r in rv["readability"]:
            st.write("✅", r)

    else:
        st.info("Upload resume.")




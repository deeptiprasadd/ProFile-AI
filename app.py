import re
import math
import collections
from typing import Dict, List, Tuple

import streamlit as st
import fitz  # PyMuPDF
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt

st.set_page_config(page_title="ATS Resume App", page_icon="📄", layout="wide")


# ======================================================
# PDF TEXT READER
# ======================================================
def read_uploaded_file(file) -> str:
    if not file:
        return ""
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        return text
    except Exception:
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

        if line.isupper() or any(h in line.lower() for h in SECTION_TOKENS):
            cleaned.append("\n" + line.upper())
            continue

        if re.match(r"^[•\-\*]", line):
            cleaned.append("  - " + line.lstrip("•-* ").strip())
        else:
            cleaned.append(line)
    return "\n".join(cleaned)


# ======================================================
# LEXICONS
# ======================================================
ACTION_VERBS = {
    "built","designed","led","optimized","automated","deployed","shipped",
    "improved","analyzed","implemented","integrated","scaled","reduced","increased",
    "architected","launched","refactored","delivered","spearheaded","orchestrated"
}

SKILL_LEXICON = {
    "Programming": {"python","java","c++","c","javascript","typescript","r","go","sql"},
    "Data/ML": {"pandas","numpy","matplotlib","scikit-learn","sklearn","tensorflow","pytorch","keras","xgboost","nlp","computer vision","cv"},
    "BI/Analytics": {"excel","power bi","tableau","dashboard","kpi","a/b testing","experimentation"},
    "Backend/Web": {"flask","fastapi","django","api","rest","graphql","node"},
    "DevOps/MLOps": {"git","docker","kubernetes","mlops","ci/cd","github actions"},
    "Cloud/DB": {"aws","gcp","azure","mysql","postgresql","snowflake","bigquery","redshift","mongodb"},
}

STOPWORDS = set((
    "a an the and or of for to with in on at as by from into over under about across between "
    "is are was were be being been it this that these those you your our their i me my we us "
    "he she they them his her its who which what where when why how not than then also etc "
    "using use used via per based including include includes".split()
))


# ======================================================
# HELPERS
# ======================================================
def words(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z\+\#\-]{1,}", text.lower())


def extract_skills(text: str) -> Dict[str, List[str]]:
    low = text.lower()
    found: Dict[str, List[str]] = {}
    for cat, items in SKILL_LEXICON.items():
        hits = []
        for it in items:
            if " " in it:
                if it in low:
                    hits.append(it)
            else:
                if re.search(fr"\b{re.escape(it)}\b", low):
                    hits.append(it)
        if hits:
            found[cat] = sorted(list(set(hits)))
    return found


def detect_missing_sections(text: str) -> List[str]:
    low = text.lower()
    missing = []
    if "summary" not in low:
        missing.append("Add a 2–3 line Professional Summary.")
    if "project" not in low:
        missing.append("Add 2–3 strong, metric-driven projects.")
    if "education" not in low:
        missing.append("Add Education section.")
    if "skill" not in low:
        missing.append("Add Skills section.")
    if not re.search("linkedin|github", low):
        missing.append("Add LinkedIn or GitHub link.")
    return missing


# ======================================================
# ATS FORMAT ISSUES
# ======================================================
def detect_format_issues(text: str) -> List[str]:
    issues = []
    if re.search(r"\|.+\|", text): issues.append("Tables detected — replace with plain bullets.")
    if re.search(r"●|■|◆|▶|▪", text): issues.append("Fancy bullets — use '-' or '*'.")
    return issues


# ======================================================
# ATS BREAKDOWN (FULL 100-POINT SYSTEM)
# ======================================================
def ats_breakdown(text: str, exp_level: str):
    fmt_issues = detect_format_issues(text)

    # Scores
    fmt_score = 20 - min(8, 2 * len(fmt_issues))
    found = extract_skills(text)
    skills_score = min(20, 4 * len(found))
    keyword_score = min(15, int(1.5 * sum(len(v) for v in found.values())))
    verbs = sum(1 for v in ACTION_VERBS if v in text.lower())
    exp_score = min(20, min(10, verbs) + (5 if "experience" in text.lower() else 0))
    metrics_score = min(15, len(re.findall(r"\b\d+(?:\.\d+)?%?\b", text)))

    seniority_score = 10
    total = fmt_score + skills_score + keyword_score + exp_score + metrics_score + seniority_score
    total = min(100, max(0, total))

    breakdown = {
        "Formatting": fmt_score,
        "Skills Relevance": skills_score,
        "Keyword Coverage": keyword_score,
        "Experience Strength": exp_score,
        "Metrics/Impact": metrics_score,
        "Seniority Alignment": seniority_score,
    }

    tips = []
    if fmt_issues:
        tips += fmt_issues
    if skills_score < 16:
        tips.append("Add more technical and domain skills.")
    if keyword_score < 12:
        tips.append("Add missing skills in work experience bullets.")
    if exp_score < 16:
        tips.append("Use action verbs + metrics in bullets.")
    if metrics_score < 10:
        tips.append("Add measurable achievements (%, numbers, time saved).")

    return total, breakdown, tips


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
# FIXED: LOCAL VISUAL IMPROVEMENT SUGGESTION
# ======================================================
def generate_layout_suggestion():
    img = Image.new("RGB", (900, 350), "#f5f5f5")
    draw = ImageDraw.Draw(img)

    draw.rectangle((20, 20, 880, 330), fill="white")
    draw.text((40, 40), "Resume Layout Suggestion", fill="black")

    draw.text((40, 90), "• Keep 1-inch margin on all sides", fill="gray")
    draw.text((40, 130), "• Use consistent font size (10–12)", fill="gray")
    draw.text((40, 170), "• Use clear sections: Summary | Skills | Experience | Projects | Education", fill="gray")
    draw.text((40, 210), "• Use bullets with action verbs + metrics", fill="gray")
    draw.text((40, 250), "• Avoid tables, columns, shapes, and icons (ATS can't read them)", fill="gray")

    return img


# ======================================================
# VISUAL INSIGHTS
# ======================================================
def plot_skills_radar(found):
    cats = list(SKILL_LEXICON.keys())
    vals = [len(found.get(c, [])) for c in cats]
    cats2 = cats + [cats[0]]
    vals2 = vals + [vals[0]]

    fig = plt.figure(figsize=(5,5))
    ax = fig.add_subplot(111, polar=True)
    angles = [n / len(cats) * 2 * math.pi for n in range(len(cats))]
    angles += angles[:1]
    ax.plot(angles, vals2)
    ax.fill(angles, vals2, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, fontsize=9)
    st.pyplot(fig)


def plot_top_words(text):
    tokens = [w for w in words(text) if w not in STOPWORDS and len(w) > 2]
    counts = collections.Counter(tokens).most_common(10)
    if not counts:
        st.info("Not enough content for word chart.")
        return

    labels, vals = zip(*counts)
    fig = plt.figure(figsize=(6,3))
    plt.bar(range(len(vals)), vals)
    plt.xticks(range(len(labels)), labels, rotation=45)
    st.pyplot(fig)


# ======================================================
# RECRUITER VIEW
# ======================================================
def recruiter_view(text: str):
    bullets = re.findall(r"(?:^|\n)\s*(?:•|\-|\*)\s*(.+)", text)
    metrics = re.findall(r"\b\d+(?:\.\d+)?%?\b", text)

    skills = extract_skills(text)
    top_skills = sorted(
        ((cat, len(v)) for cat, v in skills.items()),
        key=lambda x: -x[1]
    )[:3]

    read = []
    if len(bullets) < 6:
        read.append("Add 6–10 action verb based bullets.")
    if len(metrics) < 3:
        read.append("Add at least 3 measurable outcomes.")
    if "summary" not in text.lower():
        read.append("Add a professional summary at top.")

    return {
        "top_skills": [f"{c} ({n})" for c, n in top_skills] or ["Add more technical skills."],
        "quick_reads": bullets[:5],
        "readability": read,
    }


# ======================================================
# UI
# ======================================================
st.title("📄 Advanced ATS Resume Analyzer")

with st.sidebar:
    st.header("Upload")
    file = st.file_uploader("Upload PDF Resume")
    exp_level = st.selectbox("Experience Level", ["Fresher","Intern","1+ Years","5+ Years"])
    btn = st.button("Analyze", type="primary")

resume = ""
if btn and file:
    resume = read_uploaded_file(file)

tabs = st.tabs(["Preview","ATS Score","Missing Sections","AI Resume","Auto-filled Template","Insights","Recruiter View"])


# ======================================================
# PREVIEW TAB
# ======================================================
with tabs[0]:
    st.subheader("Structured Resume Preview")
    if resume:
        st.text_area("Parsed Resume", clean_preview_text(resume), height=360)
    else:
        st.info("Upload a resume.")


# ======================================================
# ATS SCORE TAB
# ======================================================
with tabs[1]:
    if resume:
        st.subheader("ATS Score & Breakdown")
        total, breakdown, tips = ats_breakdown(resume, exp_level)

        st.image(draw_half_gauge(total))

        st.write("### Breakdown")
        for k, v in breakdown.items():
            st.write(f"**{k}**: {v}")

        st.write("### Suggestions")
        for t in tips:
            st.write("✅", t)

    else:
        st.info("Upload resume to compute ATS score.")


# ======================================================
# MISSING SECTIONS TAB
# ======================================================
with tabs[2]:
    st.subheader("Missing Resume Sections")
    if resume:
        for m in detect_missing_sections(resume):
            st.write("✅", m)

        st.subheader("Visual Improvement Suggestion")
        st.image(generate_layout_suggestion())

    else:
        st.info("Upload resume to analyze.")


# ======================================================
# AI RESUME TAB
# ======================================================
def generate_ai_resume(text):
    img = Image.new("RGB", (950, 1300), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle((40, 40, 910, 1260), fill="#f5f5f5")
    draw.text((60, 60), "AI-Improved Resume Preview", fill="black")

    sections = {
        "SUMMARY": text[:220] or "Add a 2–3 line summary.",
        "SKILLS": "Python • SQL • ML • Power BI",
        "EXPERIENCE": "Add action verbs + measurable outcomes.",
        "EDUCATION": "Add degree + institution + year."
    }

    y = 150
    for h, c in sections.items():
        draw.rectangle((60, y, 890, y+220), fill="white")
        draw.text((80, y+10), h, fill="black")
        draw.multiline_text((80, y+60), c, fill="gray", spacing=6)
        y += 240

    return img

with tabs[3]:
    if resume:
        st.image(generate_ai_resume(resume))
    else:
        st.info("Upload resume to view AI-generated preview.")


# ======================================================
# TEMPLATE TAB
# ======================================================
def auto_fill_template(text):
    names = re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", text)
    name = names[0] if names else "FULL NAME"

    skills = re.findall(r"python|sql|excel|power bi|tableau|ml|pandas|numpy", text.lower())
    skill_set = ", ".join(sorted(set(skills))) or "Technical Skills Not Detected"

    return f"""
-----------------------------------------
| {name} |
| Auto-Filled Resume Template           |
-----------------------------------------

SUMMARY
Motivated professional skilled in {skill_set}.

SKILLS
• {skill_set}

PROJECTS
• Add measurable project details

EDUCATION
• Add degree, institute, year
"""

with tabs[4]:
    if resume:
        st.code(auto_fill_template(resume))
    else:
        st.info("Upload a resume.")


# ======================================================
# INSIGHTS TAB
# ======================================================
with tabs[5]:
    if resume:
        found = extract_skills(resume)
        st.write("### Skills Radar Chart")
        plot_skills_radar(found)

        st.write("### Most Frequent Words")
        plot_top_words(resume)

    else:
        st.info("Upload resume.")


# ======================================================
# RECRUITER VIEW TAB
# ======================================================
with tabs[6]:
    if resume:
        rv = recruiter_view(resume)

        st.write("### Top Skills Recruiters Will Notice")
        for s in rv["top_skills"]:
            st.write("•", s)

        st.write("### First 5 Bullets Recruiters See")
        if rv["quick_reads"]:
            for b in rv["quick_reads"]:
                st.write("•", b.strip())
        else:
            st.write("• Add bullet points.")

        st.write("### Readability Suggestions")
        for r in rv["readability"]:
            st.write("✅", r)

    else:
        st.info("Upload resume.")

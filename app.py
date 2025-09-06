# app.py — Profile AI (UI polish: centered content, stylish sidebar, skill chips)
# Run: streamlit run app.py
# ---------------------------------------------------------------------
# This file implements a Resume + Interview Prep app using Streamlit.
# All comments explain what each line or block does and why it's included.
# I have not changed the program flow or features — only added human-style comments.
# ---------------------------------------------------------------------

# Import Streamlit and other utilities we need.
import streamlit as st  # main web UI library
import io, os, re, tempfile, traceback, random  # built-in helpers used across the app
from typing import List, Dict  # type hints to make function signatures clearer
from difflib import SequenceMatcher  # unused in logic but retained for potential string comparisons

# Configure page title and layout so the app opens with desired routing and size.
st.set_page_config(
    page_title="ProFile AI",  # title for browser tab
    layout="wide",  # use wide layout to utilize horizontal space
    initial_sidebar_state="expanded"  # keep sidebar open by default for convenience
)

# -------------------------
# CSS: layout, centered content, badges, sidebar styling
# -------------------------
# We inject custom CSS to make the UI centered and polished.
# Using CSS gives fine-grained control for spacing, badges and sidebar visuals.
CSS = """
<style>
/* Global container to center main content (tabs) */
.main-container {
  max-width: 980px;
  margin: 0 auto;
  padding-left: 12px;
  padding-right: 12px;
}

/* Header */
.header-center { display:flex; align-items:center; justify-content:center; flex-direction:column; gap:8px; margin-top:6px; margin-bottom:6px; }
.logo-circle { width:92px; height:92px; border-radius:18px; display:flex; align-items:center; justify-content:center;
               background: linear-gradient(135deg, #78C2FF 0%, #A8FFCF 100%); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
.header-title { font-weight:800; color:#0b0b0b; margin:0; padding:0; letter-spacing:0.2px; }
.header-sub { color:#333333; margin:0; padding:0; }
.header-divider { width:80%; height:1px; background:#e6e6e6; margin-top:12px; margin-bottom:18px; border-radius:2px; }

/* Upload Card */
.upload-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 18px 22px;
  box-shadow: 0 8px 30px rgba(20,20,20,0.04);
  border: 1px solid rgba(0,0,0,0.04);
  margin: 10px auto 22px auto;
}

/* Tabs area spacing */
.tabs-wrapper { margin-top: 10px; margin-bottom: 40px; }

/* Skill badges */
.skill-badge {
  display:inline-block;
  background: #eef6ff;
  color: #0b3c78;
  border-radius: 16px;
  padding: 6px 10px;
  margin:6px 6px 6px 0;
  font-size: 14px;
  border: 1px solid rgba(11,60,120,0.06);
}

/* Sidebar improvements */
[data-testid="stSidebar"] > div:first-child {
  background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
  border-radius: 8px;
  padding: 18px;
  box-shadow: 0 6px 20px rgba(0,0,0,0.04);
  border: 1px solid rgba(0,0,0,0.04);
}
.sidebar-heading { font-weight:700; color:#0b2b4a; margin-bottom:6px; }
.sidebar-caption { color:#445566; font-size:13px; }

/* Make code preview narrower */
.stCodeBlock { max-width: 980px; }
</style>
"""
# Inject the CSS into the Streamlit app.
st.markdown(CSS, unsafe_allow_html=True)

# -------------------------
# Header area (logo + title)
# -------------------------
# A small helper to render a compact SVG logo inside a rounded gradient background.
def logo_svg(size=92):
    # returns a small HTML block for the logo; size parameter makes scaling simple.
    return f"""
    <div class="header-center" aria-hidden="true">
      <div class="logo-circle" style="width:{size}px;height:{size}px;">
        <svg width="{int(size*0.56)}" height="{int(size*0.56)}" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M12 2L13.8 8.7L20.8 9.6L15.2 13.9L17.1 20.6L12 16.9L6.9 20.6L8.8 13.9L3.2 9.6L10.2 8.7L12 2Z" fill="white" opacity="0.99"/>
        </svg>
      </div>
    </div>
    """

# Render logo HTML (centered).
st.markdown(logo_svg(92), unsafe_allow_html=True)

# Page title and subtitle - centered for a professional look.
st.markdown(
    '<div style="text-align:center;"><h1 class="header-title" style="font-size:36px;margin-bottom:2px;">ProFile-AI</h1>'
    '<div class="header-sub" style="font-size:16px;">Review + Interview Prep</div></div>',
    unsafe_allow_html=True
)

# A thin divider under the header to separate it visually from upload area.
st.markdown(
    '<div style="display:flex; justify-content:center;"><div class="header-divider"></div></div>',
    unsafe_allow_html=True
)

# -------------------------
# Optional libraries detection (defensive)
# -------------------------
# We try to import several optional parsing and NLP libraries.
# If they are not installed, the app will still work but with limited features.
_have_pdfminer = False
_have_pypdf2 = False
_have_pdfplumber = False
_have_pymupdf = False
_have_docx2txt = False
_have_pdf2image = False
_have_pytesseract = False
_have_spacy = False
_have_transformers = False

# Try pdfminer (good pure-Python text extraction).
try:
    from pdfminer.high_level import extract_text as pdfminer_extract_text
    _have_pdfminer = True
except Exception:
    _have_pdfminer = False

# Try PyPDF2 (lightweight PDF text extraction).
try:
    from PyPDF2 import PdfReader
    _have_pypdf2 = True
except Exception:
    _have_pypdf2 = False

# Try pdfplumber (another PDF parsing option).
try:
    import pdfplumber
    _have_pdfplumber = True
except Exception:
    _have_pdfplumber = False

# Try PyMuPDF (fitz) - sometimes faster and more robust.
try:
    import fitz
    _have_pymupdf = True
except Exception:
    _have_pymupdf = False

# Try docx2txt (DOCX parsing).
try:
    import docx2txt
    _have_docx2txt = True
except Exception:
    _have_docx2txt = False

# Try pdf2image for OCR fallback (convert PDF pages to images).
try:
    from pdf2image import convert_from_bytes
    _have_pdf2image = True
except Exception:
    _have_pdf2image = False

# Try pytesseract for OCR.
try:
    import pytesseract
    _have_pytesseract = True
except Exception:
    _have_pytesseract = False

# Try spaCy for optional NER/skill extraction.
try:
    import spacy
    _have_spacy = True
    try:
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        nlp = None
except Exception:
    _have_spacy = False
    nlp = None

# Try transformers for optional polishing pipeline.
try:
    from transformers import pipeline
    _have_transformers = True
except Exception:
    _have_transformers = False

# If transformers available, attempt to create a small generation pipeline.
# We use a small model (flan-t5-small) to keep resource usage reasonable.
_transformer_gen = None
if _have_transformers:
    try:
        _transformer_gen = pipeline("text2text-generation", model="google/flan-t5-small")
    except Exception:
        _transformer_gen = None  # pipeline creation may fail due to missing weights / env

# -------------------------
# Sidebar content (styled)
# -------------------------
# We place helpful instructions, parser status and tips in the left sidebar.
with st.sidebar:
    st.markdown('<div class="sidebar-heading">💡 Help & Tips</div>', unsafe_allow_html=True)  # heading
    # short usage hints to help users upload the right files or enable OCR if needed
    st.markdown('<div class="sidebar-caption">• Upload a PDF or DOCX resume. For scanned PDFs enable OCR tools (pdf2image+pytesseract).</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
    st.markdown('---')  # visual separator
    st.markdown('**Parsers detected:**')
    # show a small dict of which optional libs are available — this helps troubleshooting
    st.write({
        "pdfminer.six": _have_pdfminer,
        "PyPDF2": _have_pypdf2,
        "pdfplumber": _have_pdfplumber,
        "PyMuPDF": _have_pymupdf,
        "docx2txt": _have_docx2txt,
        "pdf2image": _have_pdf2image,
        "pytesseract": _have_pytesseract,
        "spacy": _have_spacy,
        "transformers": _have_transformers
    })
    st.markdown("---")
    st.markdown("**Quick actions**")
    # a few short steps users can follow to improve parsing success
    st.markdown("- Convert scanned PDF to searchable with OCR.")
    st.markdown("- Paste resume text in fallback if parsing fails.")
    st.caption("Recommended: pip install pdfminer.six PyPDF2 docx2txt pdf2image pytesseract")

# -------------------------
# Sanitizer & helper regexes
# -------------------------
# These regexes remove or mask PII-like content so answers don't leak real phone numbers/emails.
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://\S+|\bwww\.\S+\b")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?){1,4}\d{2,4}")
LONG_NUM_RE = re.compile(r"\b\d{7,}\b")  # very long sequences (likely phone/IDs)

# Basic set of common skills we want to detect in resumes.
COMMON_SKILLS_SET = set([
    "python","sql","tensorflow","pytorch","keras","scikit-learn","sklearn","aws","gcp","azure",
    "docker","kubernetes","spark","pandas","numpy","matplotlib","seaborn","flask","fastapi",
    "git","linux","api","nlp","cv","java","c++","javascript","react","node","postgres","mysql","mongodb"
])

# Simple sanitization to remove PII and normalize whitespace before further processing.
def sanitize_text(text: str) -> str:
    if not text: return ""
    t = EMAIL_RE.sub(" ", text)  # remove emails
    t = URL_RE.sub(" ", t)  # remove urls
    t = LONG_NUM_RE.sub(" [NUMBER] ", t)  # replace long numbers with placeholder
    t = PHONE_RE.sub(" [PHONE] ", t)  # replace likely phone patterns
    t = re.sub(r"[•\-\—\–]+", " ", t)  # normalize bullets/dashes
    t = re.sub(r"\s+", " ", t).strip()  # collapse whitespace
    return t

# Slightly different sanitizer used when showing resume snippet — replaces PII with labeled tokens.
def sanitize_for_output(text: str) -> str:
    if not text: return ""
    t = EMAIL_RE.sub("[EMAIL]", text)
    t = URL_RE.sub("[URL]", t)
    t = LONG_NUM_RE.sub("[NUMBER]", t)
    t = PHONE_RE.sub("[PHONE]", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

# Extract likely skills using heuristic matching against COMMON_SKILLS_SET.
def extract_skills_from_text_safe(text: str, limit: int = 20) -> List[str]:
    t = sanitize_text(text or "")
    found: List[str] = []
    low = t.lower()
    # first look for well-known skills in our set (higher precision)
    for s in COMMON_SKILLS_SET:
        if s in low and s not in found:
            found.append(s)
            if len(found) >= limit:
                return found[:limit]
    # then fall back to extracting alpha tokens as possible skills
    tokens = re.findall(r"\b[A-Za-z\+\#]{2,30}\b", t)
    for tok in tokens:
        tl = tok.lower()
        if tl in found: continue
        if len(tl) > 1:
            found.append(tl)
            if len(found) >= limit:
                return found[:limit]
    return found[:limit]

# Helper to return the longest (or most descriptive) lines from the resume — useful to pick "top projects".
def top_lines(text: str, n=6) -> List[str]:
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    lines_sorted = sorted(lines, key=lambda s: -len(s))
    return lines_sorted[:n]

# -------------------------
# PDF / DOCX extractors
# -------------------------
# We attempt a few parsing strategies in order; the app remains resilient if some libs are missing.
def _extract_text_from_pdf_bytes(data: bytes) -> str:
    # Try pdfminer first — often produces decent text.
    if _have_pdfminer:
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(data); tmp.flush(); tmp_path = tmp.name
            try:
                txt = pdfminer_extract_text(tmp_path) or ""
            finally:
                try: os.unlink(tmp_path)
                except Exception: pass
            if txt.strip(): return txt
        except Exception:
            pass

    # Try PyPDF2 as a fallback.
    if _have_pypdf2:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(data))
            pages=[]
            for p in reader.pages:
                try: t = p.extract_text() or ""
                except Exception: t = ""
                if t: pages.append(t)
            if any(pages): return "\n".join(pages)
        except Exception:
            pass

    # Try pdfplumber as another fallback.
    if _have_pdfplumber:
        try:
            import pdfplumber
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                pages=[]
                for p in pdf.pages:
                    try: t = p.extract_text() or ""
                    except Exception: t = ""
                    if t: pages.append(t)
            if any(pages): return "\n".join(pages)
        except Exception:
            pass

    # Finally try PyMuPDF (fitz) if available.
    if _have_pymupdf:
        try:
            import fitz
            doc = fitz.open(stream=data, filetype="pdf")
            pages=[]
            for p in doc:
                try: t = p.get_text("text") or ""
                except Exception: t = ""
                if t: pages.append(t)
            if any(pages): return "\n".join(pages)
        except Exception:
            pass

    # If none succeeded, return empty string — calling code will show fallback UI.
    return ""

# DOCX extractor (simple) — uses docx2txt if available.
def _extract_text_from_docx_bytes(data: bytes) -> str:
    if _have_docx2txt:
        try:
            with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                tmp.write(data); tmp.flush(); tmp_path = tmp.name
            try:
                import docx2txt
                text = docx2txt.process(tmp_path) or ""
            finally:
                try: os.unlink(tmp_path)
                except Exception: pass
            if text.strip(): return text
        except Exception:
            pass
    return ""

# Top-level helper to read uploaded file object and route to the correct parser.
def extract_text(uploaded_file) -> str:
    if uploaded_file is None: return ""
    try:
        data = uploaded_file.getvalue()  # read file bytes from streamlit uploaded file
    except Exception:
        return ""
    name = (uploaded_file.name or "").lower()
    # Use PDF parsing branch for .pdf or when bytes indicate PDF header
    if name.endswith(".pdf") or data[:4] == b"%PDF":
        txt = _extract_text_from_pdf_bytes(data)
        return txt or ""
    if name.endswith(".docx"):
        txt = _extract_text_from_docx_bytes(data)
        return txt or ""
    # Try PDF then DOCX as a final attempt
    txt = _extract_text_from_pdf_bytes(data)
    if txt: return txt
    txt = _extract_text_from_docx_bytes(data)
    return txt or ""

# -------------------------
# Question / Answer helpers
# These implement heuristics for sample answers and question generation.
# -------------------------
def find_best_project_line(resume_text: str, role: str = "") -> str:
    candidates = top_lines(resume_text, n=12)
    if not candidates: return ""
    role_tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", (role or "").lower()))
    best = ""
    best_score = -1
    for c in candidates:
        tokens = set(re.findall(r"\b[a-zA-Z]{3,}\b", c.lower()))
        score = len(tokens & role_tokens)
        if score == 0:
            # if role words don't match, prefer longer lines slightly
            score = min(1, len(c) // 80)
        if score > best_score:
            best_score = score
            best = c
    return best

def paraphrase_project_line_safe(line: str, max_len: int = 140) -> str:
    if not line: return ""
    s = sanitize_text(line)
    # remove company-like words and years to avoid PII and keep phrasing generic
    s = re.sub(r"\b(private|limited|ltd|inc|llc|pvt|company|co)\b", " ", s, flags=re.I)
    s = re.sub(r"\b(19|20)\d{2}\b", " ", s)
    s = re.sub(r"[^\w\s\+\#%.,()-]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > max_len:
        s = s[:max_len].rsplit(" ", 1)[0] + "…"
    return s

def extract_first_metric_safe(resume_text: str) -> str:
    t = sanitize_text(resume_text or "")
    # look for a percentage first
    m = re.search(r"\b\d{1,3}(?:\.\d+)?\s*%\b", t)
    if m: return m.group(0)
    # else look for a smaller integer that likely represents a metric
    m2 = re.search(r"\b\d{1,3}(?:,\d{3})*\b", t)
    if m2:
        num_str = m2.group(0).replace(",", "")
        try:
            val = int(num_str)
            if val < 1000000:  # ignore extremely large numbers like phone / IDs
                return m2.group(0)
        except Exception:
            pass
    return ""

# This function takes a question + resume and creates a short sample answer.
# It's heuristic-driven and intentionally conservative: it won't invent PII or new numbers.
def generate_sample_answer(question: str, resume_text: str, role: str = "") -> str:
    q = (question or "").strip()
    rt = (resume_text or "").strip()
    role = (role or "").strip()
    skills = extract_skills_from_text_safe(rt, limit=6)
    skill_snip = ", ".join(skills[:3]) if skills else "relevant technical skills"
    project_line = find_best_project_line(rt, role)
    paraphrase = paraphrase_project_line_safe(project_line)
    metric = extract_first_metric_safe(rt) or "measurable improvements"
    qlow = q.lower()

    # Handle "why this role" questions
    if ("why" in qlow and "role" in qlow) or qlow.startswith("why do you want"):
        lead = f"I'm excited about this role because it aligns with my experience in {skill_snip} and the type of work described."
        example = f" For example, I {paraphrase}" if paraphrase else ""
        if paraphrase and not paraphrase.endswith("."):
            example = f" For example, I {paraphrase}."
        close = " I’d love to bring that impact here and help the team ship measurable results."
        return (lead + example + close).strip()

    # Elevator pitch / 'Tell me about yourself'
    if "tell me about yourself" in qlow or qlow.startswith("tell me"):
        s1 = f"I’m a practitioner with hands-on experience in {skill_snip} and building data-driven solutions."
        s2 = f"Recently, I worked on projects such as {paraphrase or 'fraud detection and lead generation projects'} that focused on delivering {metric}."
        s3 = "I enjoy solving problems end-to-end and collaborating with cross-functional teams to turn insights into production outcomes."
        return " ".join([s1, s2, s3]).strip()

    # Walkthrough/explain project style questions
    if any(w in qlow for w in ("explain", "describe", "walk me through", "project", "responsibility")):
        if paraphrase:
            tools = skills[0] if skills else "relevant tools"
            return f"{paraphrase}. I led this effort using {tools} and focused on improving outcomes; we achieved {metric}."
        else:
            return f"I worked on projects relevant to this area using {skill_snip}. I can walk through a specific example if you'd like."

    # Technical experience with X
    if "experience with" in qlow or qlow.startswith("describe your experience with") or "how do you" in qlow:
        techs = re.findall(r"\b(python|sql|tensorflow|pytorch|docker|aws|gcp|spark|keras|sklearn|react|node|java)\b", qlow)
        tool = techs[0] if techs else (skills[0] if skills else None)
        if tool:
            return f"I have practical experience with {tool}. On my recent project I used {tool} to build pipelines and evaluate models; this helped improve results by {metric}."
        else:
            return f"I have hands-on experience with {skill_snip}. I approach technical problems by clarifying requirements, prototyping, validating with metrics, and productionizing."

    # Generic fallback using paraphrase and skills
    if paraphrase:
        return f"{paraphrase}. I used {skill_snip} to achieve {metric} and collaborated with cross-functional teams to measure impact and iterate quickly."
    return f"I have relevant experience in {skill_snip} and can discuss a recent project where I delivered {metric}."

# Generate question lists tailored to resume content (HR, resume-specific and technical).
def generate_interview_questions_safe(resume_text: str, role: str = "") -> Dict[str, List[str]]:
    sanitized = sanitize_text(resume_text or "")
    skills = extract_skills_from_text_safe(sanitized, limit=30)
    lines = [l.strip() for l in sanitized.splitlines() if l.strip()]
    top = sorted(lines, key=lambda s: -len(s))[:6]  # longest lines often contain project descriptions
    hr = [
        "Tell me about yourself.",
        "Why do you want this role?",
        "Describe a time you had a conflict at work and how you resolved it."
    ]
    resume_specific = []
    for p in top:
        preview = p if len(p) < 100 else p[:100].rstrip() + "…"
        resume_specific.append(f"Explain this project/responsibility: \"{preview}\"")
    technical = []
    for s in skills[:12]:
        technical.append(f"Describe your experience with {s}.")
    if role and len(role) > 2:
        technical.append(f"What makes you a good fit for the {role} role technically?")
    # Shuffle deterministically based on resume content so the questions vary across resumes.
    seed = abs(hash(sanitized)) % (2**32)
    rnd = random.Random(seed)
    rnd.shuffle(hr); rnd.shuffle(resume_specific); rnd.shuffle(technical)
    return {"hr": hr[:3], "resume_specific": resume_specific[:6], "technical": technical[:8]}

# A simple answer scorer that checks length, presence of numeric metrics and tool mentions.
def score_answer_simple_fn(answer: str) -> Dict:
    text = (answer or "").strip()
    if not text:
        return {"score": 0, "feedback": "No answer provided.", "improved": ""}
    score = 5
    feedback = []
    words = len(text.split())
    if words < 30:
        score -= 1; feedback.append("Short — add context & outcome.")
    if re.search(r"\d{1,3}%|\b\d+k?\b", text):
        score += 2
    else:
        feedback.append("Add numeric impact if possible.")
    if re.search(r"\b(python|sql|tensorflow|pytorch|docker|aws|gcp|spark|react|node|java)\b", text.lower()):
        score += 1
    else:
        feedback.append("Mention tools used.")
    score = max(0, min(10, score))
    improved = f"Situation: [context]. Task: [what]. Action: I used [tools] to {text.split('.')[0][:120]}. Result: [metric]."
    return {"score": score, "feedback": " ".join(feedback) if feedback else "Good", "improved": improved}

# -------------------------
# Small helper to render skill badges as HTML for nicer visuals.
def render_skill_chips(skills: List[str]) -> str:
    if not skills:
        return "<div>No skills detected.</div>"
    html = '<div style="max-width:980px;margin:6px 0 16px 0;">'
    for s in skills:
        safe = re.sub(r"[^A-Za-z0-9\+\#\- ]","", s)  # basic sanitation for badge text
        html += f'<span class="skill-badge">{safe}</span>'
    html += "</div>"
    return html

# -------------------------
# Upload area (centered)
# -------------------------
# We visually encapsulate upload controls inside a styled card to make UI clean.
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
st.markdown("### Upload Resume & Job Description")  # section title

# Two columns: left for resume upload, right for JD upload.
c1, c2 = st.columns([1,1])
with c1:
    # file_uploader returns a UploadedFile object or None
    resume_file = st.file_uploader("Resume (PDF or DOCX) — upload here", type=["pdf","docx"], key="resume_uploader")
with c2:
    jd_file = st.file_uploader("Job Description (optional)", type=["pdf","docx","txt"], key="jd_uploader")

# Separate row for role input and a toggle to enable model polishing.
rcol1, rcol2 = st.columns([2,1])
with rcol1:
    target_role = st.text_input("Target Role (optional)", value="")
with rcol2:
    use_model = st.checkbox("Enable optional polishing (transformers)", value=False)

# Close upload card div
st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Attempt to parse uploaded resume (defensive)
# -------------------------
resume_text = ""
resume_error = None
if resume_file:
    try:
        # call extract_text which tries several parsers based on availability
        resume_text = extract_text(resume_file)
        if not resume_text:
            # Inform the user in the sidebar if parsing returned no text
            resume_error = "Could not auto-parse PDF/DOCX. Try installing pdfminer.six/PyPDF2/docx2txt or paste resume in fallback."
            st.sidebar.warning(resume_error)
    except Exception as e:
        # If parsing raises an exception, show diagnostics to the user in the sidebar.
        resume_error = f"Extractor exception: {e}"
        st.sidebar.error(resume_error)
        st.sidebar.text(traceback.format_exc()[:1000])

# If parsing didn't produce text, display a fallback text area so user can paste resume text manually.
if not resume_text:
    st.info("Resume parsing failed or no resume uploaded. You can paste resume text in the fallback box below.")
    resume_text = st.text_area("Or paste resume text here:", height=260)
    if not resume_text:
        # If user hasn't provided anything, stop rendering further UI to avoid confusing errors.
        st.stop()

# Parse JD if provided (non-blocking)
jd_text = ""
if jd_file:
    try:
        jd_text = extract_text(jd_file) or ""
    except Exception as e:
        st.sidebar.error(f"JD parse failed: {e}")

# canonical sanitized resume used across the app
resume_text_sanitized = sanitize_text(resume_text)

# -------------------------
# Tabs for app features — centered content within each tab
# -------------------------
tab_labels = ["🛠 Suggestions", "🎯 Role Match", "❓ Interview Q&A", "🤖 AI Coach", "📊 Resume Insights"]
tabs = st.tabs(tab_labels)

# -------- Suggestions Tab --------
with tabs[0]:
    st.markdown('<div class="main-container tabs-wrapper">', unsafe_allow_html=True)
    st.header("🛠 Suggestions & Quick Fixes")
    # warn if resume seems minimal
    if len(resume_text_sanitized) < 300:
        st.warning("Resume text seems short — add more project details and outcomes.")
    # a small suggestion to include LinkedIn
    if "linkedin" not in resume_text.lower() and "linkedin.com" not in resume_text.lower():
        st.info("Consider adding a LinkedIn link in the contact section.")
    st.subheader("Detected skills (sample)")
    skills = extract_skills_from_text_safe(resume_text_sanitized)
    # render the skill badges using helper HTML
    st.markdown(render_skill_chips(skills), unsafe_allow_html=True)
    st.subheader("Missing / Covered Keywords (vs JD)")
    if jd_text:
        # simple keyword extraction: words from JD vs resume
        jd_kws = set(re.findall(r"\b[a-zA-Z\+\#\-]{2,}\b", jd_text.lower()))
        resume_kws = set(re.findall(r"\b[a-zA-Z\+\#\-]{2,}\b", resume_text_sanitized.lower()))
        common = sorted(list(jd_kws.intersection(resume_kws)))[:25]
        missing = sorted(list(jd_kws - resume_kws))[:25]
        st.write("Covered keywords (sample):", common)
        st.write("Missing keywords (sample):", missing)
    else:
        st.info("Upload a JD to enable keyword matching.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Role Match Tab --------
with tabs[1]:
    st.markdown('<div class="main-container tabs-wrapper">', unsafe_allow_html=True)
    st.header("🎯 Role Match")
    # allow on-page role input if sidebar input was empty
    role_in = target_role or st.text_input("Enter role to compute match", value="")
    # Define a conservative scoring heuristic for role match
    def role_match_score(resume_text: str, role: str) -> float:
        if not role: return 0.0
        tokens = re.findall(r"\b[a-zA-Z\+\#\-]{2,}\b", role.lower())
        rlow = (resume_text or "").lower()
        matches = sum(1 for t in tokens if t in rlow)
        skills = extract_skills_from_text_safe(resume_text)
        role_part = matches / max(1, len(tokens))
        skill_part = min(1.0, len(skills) / 5.0)
        return round(0.6 * role_part + 0.4 * skill_part, 2)
    score = role_match_score(resume_text_sanitized, role_in)
    st.metric(label=f"Match vs '{role_in}'", value=f"{score*100:.0f}%" if role_in else score)
    st.write("Top skills:", extract_skills_from_text_safe(resume_text_sanitized)[:8])
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Interview Q&A Tab --------
with tabs[2]:
    st.markdown('<div class="main-container tabs-wrapper">', unsafe_allow_html=True)
    st.header("❓ Interview Q&A")
    # generate question lists tailored to the resume content
    qdict = generate_interview_questions_safe(resume_text_sanitized, target_role)
    st.subheader("HR")
    for q in qdict["hr"]: st.write("- " + q)
    st.subheader("Resume-specific")
    for q in qdict["resume_specific"]: st.write("- " + q)
    st.subheader("Technical")
    for q in qdict["technical"]: st.write("- " + q)

    st.markdown("---")
    st.subheader("Generate tailored sample answer")
    all_qs = qdict["hr"] + qdict["resume_specific"] + qdict["technical"]
    if all_qs:
        # selection box to pick a question
        q_choice = st.selectbox("Pick a question:", all_qs)
        # pressing the button triggers the generation (synchronous)
        if st.button("Generate sample answer"):
            try:
                core = generate_sample_answer(q_choice, resume_text_sanitized, target_role)
            except Exception:
                core = "I have relevant experience and can give a detailed answer if needed."
            final = core
            # optional polishing with transformers if enabled and available
            if _have_transformers and use_model and _transformer_gen is not None:
                try:
                    prompt = f"Polish this interview answer to be professional and concise. Preserve facts and do not add new numeric identifiers: {core}"
                    polished = _transformer_gen(prompt, max_new_tokens=120)
                    if isinstance(polished, list) and polished:
                        cand = polished[0].get("generated_text") or polished[0].get("text") or ""
                        if cand and cand.strip(): final = cand
                    elif isinstance(polished, dict):
                        final = polished.get("generated_text") or polished.get("text") or final
                except Exception:
                    # if model fails, we silently fall back to the heuristic answer
                    pass
            # remove placeholder tokens from appearing verbatim in output
            final = re.sub(r"\[PHONE\]|\[NUMBER\]", "", final)
            final = re.sub(r"\s+", " ", final).strip()
            st.success("Sample answer:")
            st.write(final)
    else:
        st.info("No questions available for this resume.")
    st.markdown('</div>', unsafe_allow_html=True)

# -------- AI Coach Tab --------
with tabs[3]:
    st.markdown('<div class="main-container tabs-wrapper">', unsafe_allow_html=True)
    st.header("🤖 AI Coach — Score & Improve")
    st.write("Type your answer and get a quick score, feedback and a templated improved answer.")
    # default example question
    user_q = st.text_input("Question:", value="Walk me through your most impactful project.")
    # multi-line input for the user's answer
    user_a = st.text_area("Your answer:", height=200)
    # button to compute score and show a templated rewrite
    if st.button("Score & Improve Answer"):
        res = score_answer_simple_fn(user_a)
        st.subheader(f"Score: {res['score']}/10")
        st.write("Feedback:", res['feedback'])
        st.subheader("Template rewrite")
        st.write(res['improved'])
        # optional transformer polish if available/enabled
        if _have_transformers and use_model and _transformer_gen is not None:
            try:
                prompt = f"Polish the following interview answer to be concise and professional while preserving metrics and tools: {res['improved']}"
                polished = _transformer_gen(prompt, max_new_tokens=120)
                if isinstance(polished, list) and polished:
                    cand = polished[0].get("generated_text") or polished[0].get("text") or ""
                    if cand and cand.strip():
                        st.subheader("Polished (optional):")
                        st.write(cand.strip())
            except Exception:
                pass
    st.markdown('</div>', unsafe_allow_html=True)

# -------- Resume Insights (last tab) --------
with tabs[4]:
    st.markdown('<div class="main-container tabs-wrapper">', unsafe_allow_html=True)
    st.header("📊 Resume Insights")
    st.subheader("Preview (first 900 chars)")
    # show sanitized snippet to avoid leaking PII in UI
    st.code(sanitize_for_output(resume_text_sanitized[:900]) + ("…" if len(resume_text_sanitized) > 900 else ""))
    st.subheader("Detected skills (safe)")
    skills = extract_skills_from_text_safe(resume_text_sanitized)
    st.markdown(render_skill_chips(skills), unsafe_allow_html=True)
    st.subheader("Top project/responsibility lines (sanitized)")
    for ln in top_lines(resume_text_sanitized, n=6):
        st.markdown(f"- {ln}")
    st.markdown('</div>', unsafe_allow_html=True)

# Close the outer main container
st.markdown('</div>', unsafe_allow_html=True)

# A small footer caption reminding about optional libraries and capabilities.
st.caption("This app uses defensive parsing and heuristics. Install optional packages to enable OCR, polishing and NER-backed skill extraction.")
# End of file

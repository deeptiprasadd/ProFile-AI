# Profile AI 
**Live Demo:** _(optional — add your Streamlit app URL here)_  

---

## Overview  

**Profile AI** is a Streamlit-based Resume Review & Interview Preparation tool designed to help candidates improve their resumes and practice interviews faster. Users upload a resume (PDF / DOCX) and optionally a job description; the app then analyzes the resume, extracts skills and projects, suggests improvements, computes a role-match score, generates likely interview questions, and produces tailored sample answers. An AI coach provides quick scoring and templated rewrites for your spoken or written answers.  

The app is defensive by design — parsing and AI features are optional and will work even when some third-party libraries are not installed. Sensitive content (emails, phone numbers, long IDs) is sanitized automatically.  

---

## Features  

- **Upload Resume (PDF / DOCX)** and optional Job Description (JD).  
- **Resume Suggestions**: formatting hints, missing keywords (against JD), and contact/link checks.  
- **Role Match**: quick role-fit score combining keyword matches and detected skills.  
- **Interview Q&A generator**:  
  - HR questions  
  - Resume-specific questions derived from your projects  
  - Technical questions based on detected skills  
- **Sample Answer Generator**: concise, tailored answers based on your resume, polished optionally with a transformer model.  
- **AI Coach**:  
  - Paste your own answer  
  - Get a quick score (0–10)  
  - Receive feedback and a templated rewrite  
- **Resume Insights** tab:  
  - Preview of your resume text  
  - Detected skills  
  - Sanitized top project lines  
- **Fallback UI**: paste resume text manually if parsing fails.  
- **Optional OCR + NER + Transformers** for advanced parsing and answer polishing.  

---

## Quick Start  

### 1. Clone the repository  
git clone <repository_url>
cd <repository_directory>

### 2.Create and activate virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

### 3. Install dependencies
# Minimal install (core features):
pip install -r requirements.txt

### 4. Run the app
streamlit run app.py

---

## Usage

1. Upload Resume & JD: upload resume (PDF/DOCX) and optionally a JD.

2. Target Role: enter a role name to compute a role-match score.

3. Explore Tabs:

- Suggestions: improvements & keyword coverage.

- Role Match: role-fit score and top skills.

---

### Technical Workflow

[User uploads Resume / JD]  
     ↓  
extract_text() → Parse PDF/DOCX → sanitize_text()  
     ↓  
extract_skills_from_text_safe() → detect skills  
     ↓  
generate_interview_questions_safe() → HR + Resume + Technical questions  
     ↓  
generate_sample_answer() → tailored sample answers  
     ↓  
score_answer_simple_fn() → score + feedback + template rewrite  
     ↓  
[Optional] transformer pipeline → polish answers  
     ↓  
Display results across tabs (Suggestions, Role Match, Q&A, AI Coach, Insights)  

---

### Function Reference

- extract_text(file): parses PDF/DOCX (multiple fallback methods, OCR optional).

- sanitize_text(text): removes emails, phone numbers, long IDs.

- extract_skills_from_text_safe(text): detects technical skills with heuristics + spaCy (optional).

- generate_interview_questions_safe(resume, role): creates HR, resume, and technical questions.

- generate_sample_answer(question, resume, role): generates concise, tailored sample answers.

- score_answer_simple_fn(answer): evaluates user answer with a score, feedback, and improved template.

- Interview Q&A: HR, resume-specific, and technical questions with sample answers.

---

### Installation Troubleshooting

- PDF Parsing Fails: install one of pdfminer.six, PyPDF2, pdfplumber, or PyMuPDF.
- OCR Needed: install pdf2image, pytesseract, and system tesseract / poppler.
- NER-based Skills: install spacy and run python -m spacy download en_core_web_sm.
- Answer Polishing: install transformers, sentencepiece, and torch.



- AI Coach: score your answer and get rewrites.

- Resume Insights: preview, skills, and project lines.

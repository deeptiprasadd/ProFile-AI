```markdown
# ProFile: ATS Resume Analyzer

**Smart resume analysis powered by advanced parsing algorithms.**

An intelligent Streamlit platform that dissects resumes like a recruiter, identifies gaps, calculates ATS compatibility scores, and transforms your resume into a job-ready document—no AI APIs required.

Live Demo: https://ats-resume-analyzer.streamlit.app/

---

## What It Does

- Upload a PDF resume and get instant structural analysis
- Receive a 100-point ATS compatibility score with detailed breakdown
- Identify missing sections and weak points
- Generate an auto-filled, ATS-friendly resume template
- See what recruiters notice in the first 7 seconds
- Visualize keyword patterns and skill distributions

## Key Features

### 1. PDF Resume Upload
- Safe text extraction using PyPDF2
- Intelligent cleaning and formatting
- Cloud-deployment ready

### 2. ATS Score Breakdown
Comprehensive 100-point scoring system based on:
- Formatting quality
- Skills relevance
- Keyword coverage
- Experience strength
- Metrics and achievements
- Seniority alignment

### 3. Missing Sections Detector
Automatically checks for:
- Professional summary
- Skills section
- Projects
- Work experience
- Education
- LinkedIn/GitHub links

### 4. AI-Style Resume Preview
Generates a modern, card-style visual mockup of an improved resume layout.

### 5. Auto-Filled Resume Template
Extracts your information and generates a clean, ATS-optimized template ready to use.

### 6. Insights Dashboard
- Word frequency analysis
- Keyword pattern detection
- Resume language strength metrics

### 7. Recruiter View Simulation
Shows exactly what recruiters see first:
- Top skills at a glance
- Key bullet points
- Missing measurable results
- Readability warnings

## Quick Start

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_directory>
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```

Visit `localhost:8501` to start analyzing resumes.

## How to Use

1. **Upload Resume** - Drop your PDF file into the uploader
2. **Navigate Tabs** - Explore different analysis views:
   - **Preview** - Cleaned and structured resume text
   - **ATS Score** - Detailed scoring gauge with breakdown
   - **Missing Sections** - Structural gaps identified
   - **AI Resume** - Visual improvement mockup
   - **Auto Template** - Ready-to-copy ATS template
   - **Insights** - Word frequency and signal strength
   - **Recruiter View** - First-impression analysis

## Technical Workflow

```
[Upload PDF Resume]
        ↓
read_uploaded_file() → extract text (PyPDF2)
        ↓
clean_preview_text() → structured formatting
        ↓
extract_skills() → cross-check with skill lexicons
        ↓
ats_breakdown() → scoring engine (100-point system)
        ↓
generate_layout_suggestion() → visual improvement mockup
        ↓
generate_ai_resume() → card-style layout rendering
        ↓
recruiter_view() → top skills + quick-read bullets
        ↓
UI tabs → display full analysis
```

## Function Reference

### read_uploaded_file(file)
Extracts text from PDF using PyPDF2.

### clean_preview_text(text)
Cleans formatting, normalizes bullets, detects sections.

### extract_skills(text)
Detects categorized skill sets using keyword lexicons.

### detect_missing_sections(text)
Identifies missing resume sections.

### ats_breakdown(text, exp_level)
Returns ATS score with category breakdown and suggestions.

### generate_layout_suggestion()
Creates a visual resume improvement mockup.

### generate_ai_resume(text)
Creates a modern resume preview image.

### auto_fill_template(text)
Generates a simple ATS-safe template filled with your data.

### recruiter_view(text)
Simulates how recruiters interpret your resume.

## Installation Troubleshooting

### PDF Parsing Error
```bash
pip install PyPDF2
```

### Image or Gauge Not Showing
```bash
pip install pillow
```

### Charts Not Displaying
```bash
pip install matplotlib
```

### Streamlit Cloud Deployment Error
Ensure `requirements.txt` contains:
```
streamlit
PyPDF2
pillow
matplotlib
```

## Tech Stack

Streamlit • PyPDF2 • Pillow • Matplotlib • Python

## Project Structure

```
ProFile/
├── app.py
├── requirements.txt
├── README.md
└── .streamlit/
    └── config.toml
```

## License

MIT License - Feel free to use and modify.

## Contributing

Contributions are welcome! Submit a pull request or open an issue.

---

**Built with no external AI dependencies** - Works reliably in any environment.
```

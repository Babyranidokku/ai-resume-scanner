# 📄 AI Resume Scanner

An **AI-powered Resume Scanner** that automates resume parsing, skill extraction, and relevance scoring against a Job Description (JD) — built with **Python**, **spaCy**, **BERT**, and **Sentence Transformers**.

---

## 🚀 Project Overview

This project is part of my hands-on learning in **AI & NLP**. It aims to:
- Extract structured information (Name, Email, Skills, Projects) from unstructured PDF/DOCX resumes.
- Match extracted skills & projects with a given JD.
- Calculate a smart match score and generate intelligent feedback for candidates or recruiters.

---

## 🧩 Tech Stack

- **Python** (PDF processing, NLP pipelines)
- **spaCy** (NER, custom parsing)
- **PDFPlumber / Textract** (PDF/DOCX parsing)
- **BERT, Sentence-BERT** (semantic similarity)
- **Flask** (web API + UI)
- **VS Code, Jupyter**

---

## ✅ Progress & Weekly Updates

### 📅 **Week 1**
- Implemented basic PDF resume text extraction.
- Faced issues:
  - ❌ Name extraction incorrectly picked up degree names.
  - ❌ Skills were missing or merged incorrectly.
  - ❌ Initial scoring logic gave unfair results.
- ✔️ Fixes:
  - Improved regex patterns and top-line NLP rules.
  - Started custom pipelines for cleaner skill tokens.

---

### 📅 **Week 2**
- Integrated semantic matching for skills using **Sentence-BERT (MiniLM)**.
- Added project extractor with keyword filtering + cosine similarity to remove duplicates.
- Combined skill & project match to calculate total match score.
- Built simple Flask UI to show results + feedback.
- Solved issues:
  - Name parsing improved.
  - Filtered non-skill JD terms like `b.tech`.
  - Removed cluttered similarity scores from frontend.

---

### 📅 **Week 3**
- Experimented with **BERT** + **spaCy** for advanced entity recognition.
- Tested project-to-JD relevance extraction using semantic similarity.
- Integrated scoring to reflect both skills & project match.
- Challenges:
  - Still missing some skills in certain resume formats.
  - Some project entities misclassified.
  - Accuracy of match score needs fine-tuning.

---

## ⚙️ Current Limitations & Next Steps

- [ ] Improve extraction on edge cases (broken lines, unique formats).
- [ ] Train/finetune custom NER model for domain-specific skills.
- [ ] Enable JD input as PDF, not just plain text.
- [ ] Add export-to-PDF feature for report.
- [ ] Better summarization block for match count.
- [ ] Deploy a simple **Streamlit** or **Flask** demo.

---

## 💻 How to Run

```bash
# Clone the repo
git clone 
cd ai-resume-scanner

# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

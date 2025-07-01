import re
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

PROJECT_KEYWORDS = [
    "project", "developed", "built", "created", "implemented",
    "designed", "engineered", "deployed", "contributed"
]

EXCLUDE_SECTION_KEYWORDS = ["education", "mentor", "activities"]

KNOWN_SKILLS = [
    "python", "flask", "django", "tensorflow", "nlp",
    "react", "node.js", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "sql", "html", "css",
    "javascript", "transformers", "scikit-learn", "hugging face",
    "google colab", "mysql", "mongodb"
]

def extract_projects(text: str) -> List[Dict[str, List[str]]]:
    projects = []
    doc = nlp(text)

    for sentence in doc.sents:
        line = sentence.text.strip().lower()
        if any(kw in line for kw in PROJECT_KEYWORDS):
            if not any(ex_kw in line for ex_kw in EXCLUDE_SECTION_KEYWORDS):
                name = sentence.text.strip().split(":")[0][:80]
                skills = extract_skills(sentence.text)
                projects.append({"name": name, "skills": skills})

    return deduplicate_projects(projects)

def deduplicate_projects(projects: List[Dict[str, List[str]]], threshold: float = 0.8) -> List[Dict[str, List[str]]]:
    unique = []
    for p1 in projects:
        if not any(calculate_project_similarity(p1["name"], p2["name"]) > threshold for p2 in unique):
            unique.append(p1)
    return unique

def calculate_project_similarity(p1: str, p2: str) -> float:
    emb = model.encode([p1, p2])
    return np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))

def evaluate_projects_against_jd(projects: List[Dict[str, List[str]]], job_description: str) -> List[str]:
    results = []
    jd_keywords = set(job_description.lower().split())

    for project in projects:
        relevant_skills = set(project["skills"])
        if relevant_skills & jd_keywords:
            results.append(f"✅ The project '{project['name']}' uses skills relevant to the JD.")
        else:
            results.append(f"❌ The project '{project['name']}' does not directly match the JD.")
    return results

def extract_skills(text: str) -> List[str]:
    found = []
    lower_text = text.lower()
    for skill in KNOWN_SKILLS:
        if skill in lower_text:
            found.append(skill)
    return list(set(found))

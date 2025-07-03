import re
import spacy
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")

PROJECT_KEYWORDS = [
    "project", "developed", "built", "created", "implemented",
    "designed", "engineered", "deployed", "contributed",
    "system", "application", "tool", "pipeline", "framework", "model"
]

EXCLUDE_SECTION_KEYWORDS = ["education", "mentor", "activities"]

KNOWN_SKILLS = [
    "python", "flask", "django", "tensorflow", "nlp",
    "react", "node.js", "machine learning", "deep learning",
    "data analysis", "pandas", "numpy", "sql", "html", "css",
    "javascript", "transformers", "scikit-learn", "hugging face",
    "google colab", "mysql", "mongodb"
]

RELATED_SKILLS = {
    # unchanged - same mappings
    # your original RELATED_SKILLS block here
}

def extract_projects(text: str) -> List[Dict[str, List[str]]]:
    projects = []
    doc = nlp(text)
    inside_projects_section = False

    for sentence in doc.sents:
        line = sentence.text.strip()
        lower_line = line.lower()

        if "projects" in lower_line:
            inside_projects_section = True
            continue

        if inside_projects_section:
            if lower_line.startswith("-") or lower_line.startswith("•"):
                name = line[:80]
                skills = extract_skills(line)
                if skills:
                    projects.append({"name": name, "skills": skills})
                continue
            if line == "" or line.endswith(":"):
                inside_projects_section = False

        if any(kw in lower_line for kw in PROJECT_KEYWORDS) or (
            len(lower_line) < 200 and not any(ex_kw in lower_line for ex_kw in EXCLUDE_SECTION_KEYWORDS)
            and not lower_line.startswith("skills")
            and not lower_line.startswith("technologies")
            and not lower_line.startswith("expertise")
            and not lower_line.endswith(":")
        ):
            name = line.split(":")[0][:80]
            skills = extract_skills(line)
            if skills:
                projects.append({"name": name, "skills": skills})

    return deduplicate_projects(projects)

def deduplicate_projects(projects: List[Dict[str, List[str]]], threshold: float = 0.75) -> List[Dict[str, List[str]]]:
    unique = []
    seen_names = set()
    for p1 in projects:
        name_clean = p1["name"].lower().strip()
        if name_clean in seen_names:
            continue
        if not any(calculate_project_similarity(p1["name"], p2["name"]) > threshold for p2 in unique):
            unique.append(p1)
            seen_names.add(name_clean)
    return unique

def calculate_project_similarity(p1: str, p2: str) -> float:
    emb = model.encode([p1, p2])
    return np.dot(emb[0], emb[1]) / (np.linalg.norm(emb[0]) * np.linalg.norm(emb[1]))

def evaluate_projects_against_jd(projects: List[Dict[str, List[str]]], job_description: str) -> List[str]:
    results = []
    jd_keywords = get_all_jd_skills(job_description)

    for project in projects:
        project_skills = set(project["skills"])
        if project_skills & jd_keywords:
            results.append(f"✅ The project '{project['name']}' uses skills relevant to the JD.")
        else:
            results.append(f"❌ The project '{project['name']}' does not directly match the JD.")
    return results

def extract_skills(text: str) -> List[str]:
    found = set()
    lower_text = text.lower()
    for skill in KNOWN_SKILLS:
        if skill in lower_text:
            found.add(skill)
            related = RELATED_SKILLS.get(skill, [])
            for rel in related:
                found.add(rel)
    return list(found)

def get_all_jd_skills(jd_text: str) -> set:
    jd_skills = set()
    jd_lower = jd_text.lower()
    for skill in KNOWN_SKILLS:
        if skill in jd_lower:
            jd_skills.add(skill)
            related = RELATED_SKILLS.get(skill, [])
            jd_skills.update(related)
    return jd_skills

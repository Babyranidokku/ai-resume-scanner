import re
import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

TECH_SKILL_SYNONYMS = {
    "python": ["python", "py"],
    "javascript": ["javascript", "js"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "transformers": ["transformers"],
    "spaCy": ["spacy"],
    "hugging face": ["hugging face", "huggingface"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb"],
    "google colab": ["google colab"],
    "nlp": ["nlp"],
}

COMMON_IGNORE_TERMS = set([
    "experience", "team", "project", "company", "working",
    "environment", "skills", "knowledge", "understanding"
])

def normalize_skill(skill: str) -> str:
    if not skill or skill.lower() in COMMON_IGNORE_TERMS:
        return None

    cleaned = re.sub(r'[^a-zA-Z0-9+#.]', '', skill.strip().lower())
    for canonical, synonyms in TECH_SKILL_SYNONYMS.items():
        if cleaned in synonyms:
            return canonical
    return cleaned

def extract_skills(text: str) -> List[str]:
    skills = set()
    matches = re.findall(r'(?i)(?:skills|technologies|expertise)[:\-]?\s*([^\n]+)', text)
    for match in matches:
        for skill in re.split(r'[,;]', match):
            norm_skill = normalize_skill(skill.strip())
            if norm_skill:
                skills.add(norm_skill)

    doc = nlp(text)
    for chunk in doc.noun_chunks:
        norm_skill = normalize_skill(chunk.text)
        if norm_skill:
            skills.add(norm_skill)

    return list(skills)

def extract_all_skills(text: str, projects: List[str] = None) -> List[str]:
    extracted = set(extract_skills(text))
    if projects:
        for project in projects:
            extracted.update(extract_skills(project))
    return [s for s in extracted if s]

def compare_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict:
    common_skills = set(resume_skills) & set(jd_skills)
    missing_skills = set(jd_skills) - set(resume_skills)
    return {
        "common_skills": list(common_skills),
        "missing_skills": list(missing_skills)
    }

def extract_jd_skills(text: str) -> List[str]:
    doc = nlp(text)
    skills = []
    for chunk in doc.noun_chunks:
        word = chunk.text.lower()
        if word in TECH_SKILL_SYNONYMS.keys() or any(word in synonyms for synonyms in TECH_SKILL_SYNONYMS.values()):
            skills.append(word)
    return list(set(skills))

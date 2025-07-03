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
RELATED_SKILLS = {
    "deep learning": ["transformers", "bert", "lstm", "rnn", "neural networks", "sequence models"],
    "transformers": ["bert", "hugging face", "sequence models"],
    "bert": ["transformers"],
    "lstm": ["rnn", "sequence models", "deep learning"],
    "rnn": ["lstm", "sequence models", "deep learning"],
    "machine learning": ["ml", "supervised learning", "unsupervised learning", "classification", "regression"],
    "nlp": ["natural language processing", "text mining", "tokenization", "named entity recognition"],
    "spaCy": ["nlp", "ner", "entity recognition"],
    "tensorflow": ["deep learning", "keras"],
    "pytorch": ["deep learning", "torch", "nn"],
    "flask": ["fastapi", "api", "backend"],
    "fastapi": ["flask", "api", "restful"],
    "api": ["restful", "http", "backend"],
    "mongodb": ["nosql", "document db", "atlas"],
    "sql": ["mysql", "postgresql", "relational database"],
    "mysql": ["sql", "relational database"],
    "postgresql": ["sql", "relational database"],
    "javascript": ["js", "node.js"],
    "node.js": ["node", "express.js", "backend"],
    "react": ["frontend", "javascript", "jsx"],
    "html": ["css", "frontend", "web development"],
    "css": ["html", "frontend"],
    "data analysis": ["data wrangling", "data cleaning", "pandas", "numpy"],
    "hugging face": ["transformers", "bert", "token classification"],
    "google colab": ["jupyter", "notebooks", "cloud notebooks"],
    "keras": ["tensorflow", "deep learning"],
    "visualization": ["matplotlib", "seaborn", "plotly"],
}


def normalize_skill(skill: str) -> List[str]:
    if not skill:
        return []

    skill = skill.strip().lower()
    if skill in COMMON_IGNORE_TERMS:
        return []

    # Split camelCase or mixed words
    parts = re.findall(r'[a-z]+|[A-Z][a-z]*|\d+', skill)
    cleaned = []
    for part in parts:
        word = part.strip().lower()
        for canonical, synonyms in TECH_SKILL_SYNONYMS.items():
            if word in synonyms:
                cleaned.append(canonical)
    return cleaned if cleaned else [skill]

def extract_skills(text: str) -> List[str]:
    skills = set()
    matches = re.findall(r'(?i)(?:skills|technologies|expertise)[:\-]?\s*([^\n]+)', text)
    for match in matches:
        for skill in re.split(r'[,;]', match):
            for norm in normalize_skill(skill.strip()):
                skills.add(norm)

    doc = nlp(text)
    for chunk in doc.noun_chunks:
        for norm in normalize_skill(chunk.text):
            skills.add(norm)

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

    # ✅ Identify implied related skills too!
    related_skills = []
    for js in jd_skills:
        if js not in common_skills:
            for rs in resume_skills:
                if js in RELATED_SKILLS.get(rs, []):
                    related_skills.append(js)

    return {
        "common_skills": list(common_skills),
        "missing_skills": list(missing_skills - set(related_skills)),
        "related_skills": list(set(related_skills))
    }


def extract_jd_skills(text: str) -> List[str]:
    doc = nlp(text)
    skills = []
    for chunk in doc.noun_chunks:
        word = chunk.text.lower()
        if word in TECH_SKILL_SYNONYMS.keys() or any(word in synonyms for synonyms in TECH_SKILL_SYNONYMS.values()):
            skills.append(word)
    return list(set(skills))

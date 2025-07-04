import re
import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")

TECH_SKILL_SYNONYMS = {
     "python": ["python", "py"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node"],
    "express.js": ["express.js", "express"],
    "html": ["html"],
    "css": ["css"],
    "sass": ["sass", "scss"],
    "bootstrap": ["bootstrap"],
    "tailwind": ["tailwindcss", "tailwind"],
    "rest api": ["rest api", "restful api", "rest apis"],
    "graphql": ["graphql"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb"],
    "firebase": ["firebase"],
    "aws": ["aws", "amazon web services"],
    "azure": ["azure"],
    "gcp": ["gcp", "google cloud"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "tensorflow": ["tensorflow"],
    "pytorch": ["pytorch"],
    "keras": ["keras"],
    "Natural Language Processing": ["nlp", "natural language processing"],
    "Machine Learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
    "git": ["git", "github", "gitlab"],
    "jira": ["jira"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "rest": ["rest", "restful"],
    "api": ["api", "apis"],
    "linux": ["linux"],
    "unix": ["unix"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "hugging face": ["hugging face", "huggingface"],

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

# ✅ Make REVERSE lookup for synonyms
SYNONYM_LOOKUP = {}
for canonical, synonyms in TECH_SKILL_SYNONYMS.items():
    canonical_norm = canonical.strip().lower()
    SYNONYM_LOOKUP[canonical_norm] = canonical
    for syn in synonyms:
        SYNONYM_LOOKUP[syn.strip().lower()] = canonical

def normalize_skill(skill: str) -> str:
    return re.sub(r'[^a-zA-Z0-9 ]', '', skill).strip().lower()

def canonicalize(skill: str) -> str:
    norm = normalize_skill(skill)
    return SYNONYM_LOOKUP.get(norm, skill.strip().title())

def expand_for_compare(skill: str) -> List[str]:
    norm = normalize_skill(skill)
    expanded = [norm]
    for canonical, synonyms in TECH_SKILL_SYNONYMS.items():
        c_norm = normalize_skill(canonical)
        if norm == c_norm or norm in [normalize_skill(s) for s in synonyms]:
            expanded += [normalize_skill(s) for s in synonyms] + [c_norm]
    return list(set(expanded))

def extract_skills(text: str) -> List[str]:
    skills = set()

    bullet_matches = re.findall(r'[-•]\s*([A-Za-z0-9 /+.#]+)', text)
    for match in bullet_matches:
        parts = re.split(r'[,/]', match)
        for p in parts:
            norm = normalize_skill(p)
            if norm and norm not in COMMON_IGNORE_TERMS:
                skills.add(canonicalize(norm))

    matches = re.findall(r'(?i)(skills|technologies|tools)[:\-]?\s*([^\n]+)', text)
    for _, skill_line in matches:
        for skill in re.split(r'[,;/]', skill_line):
            norm = normalize_skill(skill)
            if norm and norm not in COMMON_IGNORE_TERMS:
                skills.add(canonicalize(norm))

    doc = nlp(text)
    for chunk in doc.noun_chunks:
        norm = normalize_skill(chunk.text)
        if norm and norm not in COMMON_IGNORE_TERMS:
            if norm in SYNONYM_LOOKUP:
                skills.add(canonicalize(norm))

    return list(skills)

def extract_all_skills(text: str, projects: List[str] = None) -> List[str]:
    skills = set(extract_skills(text))
    if projects:
        for p in projects:
            skills.update(extract_skills(p))
    return list(skills)

def extract_jd_skills(text: str) -> List[str]:
    return extract_skills(text)

def compare_skills(resume_skills: List[str], jd_skills: List[str]) -> Dict:
    resume_expanded = set()
    resume_canon_map = {}

    for rs in resume_skills:
        for exp in expand_for_compare(rs):
            resume_expanded.add(exp)
            resume_canon_map[exp] = canonicalize(rs)

    jd_expanded = set()
    jd_canon_map = {}

    for js in jd_skills:
        for exp in expand_for_compare(js):
            jd_expanded.add(exp)
            jd_canon_map[exp] = canonicalize(js)

    common = resume_expanded & jd_expanded
    missing = jd_expanded - resume_expanded

    # Use canonical names
    common_skills = sorted({jd_canon_map[c] for c in common})
    missing_skills = sorted({jd_canon_map[m] for m in missing})

    # Related check
    related = []
    for m in missing_skills:
        for r in resume_skills:
            if m in RELATED_SKILLS.get(r, []):
                related.append(m)
    missing_skills = list(set(missing_skills) - set(related))

    return {
        "common_skills": common_skills,
        "missing_skills": missing_skills,
        "related_skills": related
    }


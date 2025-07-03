from typing import List, Dict

def calculate_score(
    skill_comparison: Dict,
    projects: List[Dict],
    jd_text: str,
    experience: bool = True,  # adjust this in your app
    has_internship_or_achievements: bool = False  # adjust this in your app
) -> float:
    """
    Final scoring:
    - Skills: 60% base
    - Missing skills: -10% from skills portion if any
    - Experience + Projects: 20% if both, 10% if only one
    - Soft skills & style: fixed 5%
    - Achievements: fixed 5%
    """
    total_score = 0.0

    jd_skills = set(skill_comparison.get("jd_skills", []))
    common_skills = set(skill_comparison.get("common_skills", []))
    missing_skills = jd_skills - common_skills

    skills_score = 60.0
    if missing_skills:
        skills_score -= 20.0
    total_score += skills_score

    relevant_projects = sum(
        1 for project in projects if any(s in jd_skills for s in project["skills"])
    )
    projects_relevant = relevant_projects > 0

    if experience and projects_relevant:
        total_score += 20.0
    elif experience or projects_relevant:
        total_score += 10.0

    total_score += 5.0  # soft skills & outlook

    if has_internship_or_achievements:
        total_score += 5.0

    return min(max(total_score, 0), 100)

def generate_feedback(score: float, missing_skills: List[str]) -> List[str]:
    feedback = []
    if score < 60:
        feedback.append("Your profile may need improvement to match the job description.")
    if missing_skills:
        feedback.append(f"You are missing these skills: {', '.join(missing_skills)}")
    return feedback

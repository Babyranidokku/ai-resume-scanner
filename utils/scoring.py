from typing import List, Dict

def calculate_score(skill_comparison: Dict, projects: List[str], jd_text: str) -> float:
    """
    Generates a match score (0-100) based on:
    - Common skills (40%)
    - Semantic matches (30%)
    - Project alignment (30%)
    """
    score = 0.0
    
    # Skill-based scoring
    common_skills = len(skill_comparison.get('common_skills', []))
    
    # Max 40 points for exact matches (4 points per skill)
    score += min(common_skills * 4, 40)
    
    # Project-based scoring (max 30 points)
    if projects:
        score += min(len(projects) * 3, 30)  # 3 points per project
    
    return min(max(score, 0), 100)

def generate_feedback(score: float, missing_skills: List[str]) -> List[str]:
    feedback = []
    if score < 50:
        feedback.append("Consider improving your skills to match the job description.")
    if missing_skills:
        feedback.append(f"You are missing the following skills: {', '.join(missing_skills)}")
    return feedback

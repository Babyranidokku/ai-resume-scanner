from flask import Flask, request, render_template
import os
import nltk
from utils import (
    text_extraction,
    information_extraction,
    skill_extraction,
    project_extraction,
    scoring
)

# Ensure 'punkt' is available
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

# Flask App Setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Main Route
@app.route('/', methods=['GET', 'POST'])
def upload_resume():
    if request.method == 'POST':
        print("📥 POST request received")

        if 'resume' not in request.files:
            print("❌ No resume file in request")
            return render_template('upload.html', error="No file uploaded")

        resume_file = request.files['resume']
        jd_text = request.form.get('jd', '').strip()

        print(f"📄 Resume file: {resume_file.filename}")
        print(f"📝 JD text (preview): {jd_text[:60]}...")

        if resume_file.filename == '':
            return render_template('upload.html', error="No file selected")

        if not jd_text:
            return render_template('upload.html', error="Job description cannot be empty")

        if resume_file and allowed_file(resume_file.filename):
            try:
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_file.filename)
                resume_file.save(file_path)
                print(f"✅ File saved at {file_path}")

                # Read the resume content
                resume_text = text_extraction.extract_text(file_path)
                print("🔍 Starting resume processing...")

                results = process_resume_and_jd(resume_text, jd_text)
                print("✅ Processing complete, returning results.")
                return render_template('results.html', results=results)

            except Exception as e:
                print(f"❌ Exception: {e}")
                return render_template('upload.html', error=f"Error: {str(e)}")
        else:
            print("❌ Invalid file type (only PDF, DOCX, DOC, TXT allowed)")
            return render_template('upload.html', error="Invalid file type. Please upload PDF, DOCX, DOC, or TXT.")

    print("🌐 GET request received")
    return render_template('upload.html')

def process_resume_and_jd(resume_text, jd_text):
    print(f"Type of resume_text: {type(resume_text)}")
    print(f"Type of jd_text: {type(jd_text)}")

    lines = [line.strip() for line in resume_text.split('\n') if line.strip()]
    resume_info = information_extraction.extract_information(resume_text, lines)
    print(f"Type of resume_info: {type(resume_info)}")

    projects = project_extraction.extract_projects(resume_text)
    print(f"Type of projects: {type(projects)}")

    project_names = [p["name"] for p in projects]

    resume_skills = skill_extraction.extract_all_skills(resume_text, project_names)
    print(f"✅ Resume skills: {resume_skills}")

    # ✅ NEW SAFE FALLBACK!
    jd_skills = skill_extraction.extract_jd_skills(jd_text)
    if not jd_skills:
        print("⚠️ No JD skills found with extract_jd_skills, using fallback extractor...")
        jd_skills = skill_extraction.extract_skills(jd_text)
    print(f"✅ Final JD skills: {jd_skills}")

    skill_comparison = skill_extraction.compare_skills(resume_skills, jd_skills)
    print(f"✅ Skill comparison: {skill_comparison}")

    score = scoring.calculate_score(skill_comparison, projects, jd_text)
    feedback = scoring.generate_feedback(score, skill_comparison["missing_skills"])
    project_feedback = project_extraction.evaluate_projects_against_jd(projects, jd_text)

    return {
        "resume_info": resume_info,
        "common_skills": skill_comparison["common_skills"],
        "missing_skills": skill_comparison["missing_skills"],
        "projects": projects,
        "score": min(max(score, 0), 100),
        "feedback": feedback,
        "project_feedback": project_feedback
    }



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

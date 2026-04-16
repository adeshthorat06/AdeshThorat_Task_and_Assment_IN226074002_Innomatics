import re

# Define valid skills (based on job)
VALID_SKILLS = {
    "python", "machine", "learning", "sql", "nlp",
    "tensorflow", "scikit-learn", "pandas", "data"
}

def extract_skills(text):
    # Lowercase + remove symbols
    words = re.findall(r'\b[a-zA-Z\+\-]+\b', text.lower())
    
    # Keep only valid skills
    skills = set(word for word in words if word in VALID_SKILLS)
    
    return skills


def run_pipeline(resume_text, job_text):

    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)

    # Matching
    matched = resume_skills.intersection(job_skills)
    missing = job_skills - resume_skills

    # Scoring
    if len(job_skills) == 0:
        score = 0
    else:
        score = int((len(matched) / len(job_skills)) * 100)

    # Explanation
    explanation = f"""
Matched Skills: {list(matched)}
Missing Skills: {list(missing)}

Reason:
Candidate matches {len(matched)} out of {len(job_skills)} required skills.
"""

    return f"Fit Score: {score}\nJustification: {explanation}"
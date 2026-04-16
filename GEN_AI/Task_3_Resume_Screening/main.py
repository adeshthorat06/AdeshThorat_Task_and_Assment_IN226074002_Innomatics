from pipeline import run_pipeline
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load(path):
    with open(os.path.join(BASE_DIR, path), "r", encoding="utf-8") as f:
        return f.read()

job = load("data/job.txt")

resumes = {
    "Strong": load("data/strong.txt"),
    "Average": load("data/average.txt"),
    "Weak": load("data/weak.txt")
}

for name, resume in resumes.items():
    print(f"\n===== {name} =====")
    print(run_pipeline(resume, job))
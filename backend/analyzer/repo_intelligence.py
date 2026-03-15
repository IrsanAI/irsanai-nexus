import os

def calculate_repo_iq(repo_path):

    total_files = 0
    python_files = 0
    js_files = 0

    for root, dirs, files in os.walk(repo_path):
        for f in files:

            total_files += 1

            if f.endswith(".py"):
                python_files += 1

            if f.endswith(".js"):
                js_files += 1

    complexity_score = min(total_files / 50, 1.0) * 40

    language_score = 0
    if python_files > 0:
        language_score += 20
    if js_files > 0:
        language_score += 20

    repo_iq = complexity_score + language_score

    return round(repo_iq, 2)
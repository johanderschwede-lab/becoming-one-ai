"""
Compass Builder Main Script
Scans your project folder, normalizes prompt content, and writes to YAML files.
"""

import os
import yaml
from docx import Document

INPUT_DIR = "input"
OUTPUT_DIR = "output"

def normalize_text(text):
    return text.strip().replace("\n", " ")

def extract_docx(file_path):
    doc = Document(file_path)
    return "\n".join([p.text for p in doc.paragraphs])

def write_yaml(filename, content):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(os.path.join(OUTPUT_DIR, filename), "w") as f:
        yaml.dump(content, f, sort_keys=False, allow_unicode=True)

def main():
    for file in os.listdir(INPUT_DIR):
        path = os.path.join(INPUT_DIR, file)
        if file.endswith(".docx"):
            content = extract_docx(path)
        elif file.endswith(".md"):
            with open(path, encoding="utf-8") as f:
                content = f.read()
        else:
            continue

        normalized = normalize_text(content)
        write_yaml(file.replace(".", "_") + ".yaml", {
            "source_file": file,
            "content": normalized
        })

if __name__ == "__main__":
    main()

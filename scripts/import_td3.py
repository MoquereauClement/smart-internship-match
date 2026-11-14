"""Import the TD3 CSV as an explicitly labelled local replacement for the API.

Already structured fields are mapped directly. With no Ollama dependency, skill
mentions are detected using a documented fixed vocabulary, never inferred.
"""
import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "td3_sample"
VOCABULARY = {
    "Python": r"python", "JavaScript": r"javascript", "TypeScript": r"typescript",
    "Java": r"java(?!script)", "C++": r"c\+\+", "C#": r"c\#",
    "C": r"c(?!\+|\#)", "SQL": r"sql", "PostgreSQL": r"postgresql|postgres",
    "HTML": r"html(?:5)?", "CSS": r"css(?:3)?", "PHP": r"php",
    "React": r"react(?:\.js|js)?", "Node.js": r"node\.?js",
    "Unity": r"unity(?:\s*3d)?", "Git": r"git", "Docker": r"docker",
    "Linux": r"linux", "Rust": r"rust", "Power BI": r"power\s*bi",
    "Excel": r"excel", "API REST": r"api\s*rest(?:ful)?|rest\s*api",
    "Kubernetes": r"kubernetes|k8s", "TensorFlow": r"tensorflow",
    "PyTorch": r"pytorch", "AWS": r"aws", "Azure": r"azure",
    "CI/CD": r"ci\s*/\s*cd", "CMake": r"cmake", "Angular": r"angular",
    "Vue.js": r"vue\.?js", "MongoDB": r"mongodb", "Bash": r"bash",
}


def mentioned_skills(description):
    # Boundaries protect C from matching C++/C#, Git from GitHub, etc.
    return [skill for skill, pattern in VOCABULARY.items()
            if re.search(r"(?<![\w+#])(?:" + pattern + r")(?![\w+#])", description, re.IGNORECASE)]


def load_csv(path):
    offers = []
    seen = set()
    with Path(path).open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"id", "site", "title", "description", "company", "location"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("TD3 CSV is missing required columns")
        for line, row in enumerate(reader, start=2):
            if not row["id"].strip() or not row["title"].strip():
                raise ValueError(f"Missing offer id or title on CSV record {line}")
            identity = (row["site"], row["id"])
            if identity in seen:
                continue
            seen.add(identity)
            description = row["description"] or ""
            offers.append({
                "id": f"td3_{row['site']}_{row['id']}",
                "source": SOURCE, "source_site": row["site"],
                "source_file": Path(path).name,
                "provenance": "Echantillon pedagogique TD3 ; annonces issues de " + row["site"] + ". Remplacement local de France Travail, sans appel API.",
                "title": row["title"], "company": row["company"] or None,
                "location": row["location"] or None, "description": description,
                "url": row.get("job_url") or None, "date_posted": row.get("date_posted") or None,
                "publishable": False, "is_apprenticeship": None, "accessible_disability": None,
                "required_skills": mentioned_skills(description),
                "responsibilities": [], "experience_required": None, "compensation_mentioned": None,
                "extraction_method": "td3_fixed_vocabulary_v1",
                "extraction_note": "Detection de mentions techniques par vocabulaire fixe, sans IA. Missions, experience et remuneration non extraites. Une mention ne prouve pas une exigence.",
                "description_sha256": hashlib.sha256(description.encode("utf-8")).hexdigest(),
            })
    return offers


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "jobs_sample(1).csv")
    args = parser.parse_args()
    offers = load_csv(args.input)
    target = ROOT / "data/offers/td3_offers.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"offers": offers}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Keep the existing privately acquired offers and their previous IA extraction.
    # Re-import replaces only this source, making it repeatable without duplicates.
    for name in ["merged_offers.json", "structured_offers.json"]:
        path = target.parent / name
        existing = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"offers": []}
        if path.exists():
            shutil.copy2(path, path.with_suffix(".json.bak"))
        others = [o for o in existing["offers"] if o.get("source") != SOURCE]
        imported = offers if name.startswith("merged") else [{k: v for k, v in o.items() if k != "description"} for o in offers]
        existing["offers"] = others + imported
        # A previous extraction timestamp must not describe newly imported rows.
        existing.pop("generated_at", None)
        path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Imported {len(offers)} TD3 offers locally. Original platforms retained; none marked France Travail or publishable.")
    print("Skill detection: fixed vocabulary, not an Ollama extraction. Run scripts/match_offers.py next.")


if __name__ == "__main__":
    main()

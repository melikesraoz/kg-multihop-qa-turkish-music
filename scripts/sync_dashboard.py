import json
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DASHBOARD_DIR = BASE_DIR / "dashboard"
DATA_JS = DASHBOARD_DIR / "data.js"

def sync():
    print("Performing final HYBRID sync for Turkish Music Dashboard...")
    
    # 1. Benchmarks
    summary_path = OUTPUTS_DIR / "evaluation_summary_academic.json"
    benchmarks = {"labels": [], "em": [], "f1": []}
    if summary_path.exists():
        with open(summary_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Standard order for comparison
            methods = ['No-Retrieval (LLM Only)', 'Vanilla RAG', 'Vanilla QE', 'KG-Infused RAG']
            for m in methods:
                if m in data:
                    benchmarks["labels"].append(m)
                    benchmarks["em"].append(data[m].get("EM", 0))
                    benchmarks["f1"].append(data[m].get("F1", 0))

    # 2. Training Curves (provided data)
    training_curves = [
        {"epoch": 5, "train_loss": 2.10, "val_loss": 2.20, "accuracy": 0.40},
        {"epoch": 20, "train_loss": 1.25, "val_loss": 1.35, "accuracy": 0.63},
        {"epoch": 40, "train_loss": 0.80, "val_loss": 0.89, "accuracy": 0.76},
        {"epoch": 60, "train_loss": 0.57, "val_loss": 0.73, "accuracy": 0.81},
        {"epoch": 80, "train_loss": 0.47, "val_loss": 0.67, "accuracy": 0.85},
        {"epoch": 100, "train_loss": 0.43, "val_loss": 0.65, "accuracy": 0.88},
        {"epoch": 120, "train_loss": 0.41, "val_loss": 0.64, "accuracy": 0.89}
    ]

    # 3. Turkish Music Seed Entities (provided list)
    seed_entities = [
        {"id": "Q248059", "name": "Zlf Livaneli", "type": "ARTIST", "relations": 42},
        {"id": "Q660599", "name": "Arif Sa", "type": "ARTIST", "relations": 28},
        {"id": "Q334814", "name": "Erkan Qur", "type": "ARTIST", "relations": 35},
        {"id": "Q962106", "name": "Yavuz Bingl", "type": "ARTIST", "relations": 24},
        {"id": "Q6823378", "name": "Mo\u011follar", "type": "GROUP", "relations": 56},
        {"id": "Q388757", "name": "MF\u00d6", "type": "GROUP", "relations": 62},
        {"id": "Q240368", "name": "Bar\u0131\u015f Man\u00e7o", "type": "ARTIST", "relations": 88},
        {"id": "Q6093986", "name": "Cem Karaca", "type": "ARTIST", "relations": 74},
        {"id": "Q343693", "name": "Sezen Aksu", "type": "ARTIST", "relations": 112},
        {"id": "Q4156426", "name": "Ajda Pekkan", "type": "ARTIST", "relations": 95}
    ]

    # 4. XAI Detailed Trace (Music)
    trace_library = [
        {
            "id": "CASE_MUSIC_01",
            "question": "What is Zlf Livaneli's place of birth's located in the administrative territorial entity?",
            "hops": [
                {"num": "1", "title": "Birthplace Identity", "desc": "Seed: Zlf Livaneli \u2192 relation: place of birth \u2192 Result: Ilg\u0131n (Q599813)"},
                {"num": "2", "title": "Geo-Linkage", "desc": "Entity: Ilg\u0131n \u2192 relation: located in administrative entity \u2192 Result: Konya Province (Q185566)"}
            ],
            "ans": "Konya Province",
            "summary": "Zlf Livaneli was born in Ilg\u0131n, which is located in Konya Province."
        }
    ]

    # Final Data Object
    project_data = {
        "overview": {
            "entities": 5041,
            "relations": 12378,
            "paths": 84291,
            "domains": "Football \u00b7 Cinema \u00b7 Business \u00b7 Music \u00b7 Academia"
        },
        "benchmarks": benchmarks,
        "curves": training_curves,
        "seeds": seed_entities,
        "traceLibrary": trace_library,
        "lastUpdated": os.popen("date /t").read().strip() + " " + os.popen("time /t").read().strip()
    }

    content = f"// Final Compiled Dashboard Data\nconst projectData = {json.dumps(project_data, indent=4)};"
    with open(DATA_JS, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"Data package successfully compiled to {DATA_JS}")

if __name__ == "__main__":
    sync()

from pathlib import Path
import json
import csv
from itertools import combinations

input_file = Path("outputs/music_2hop_questions_draft.json")
output_tsv = Path("outputs/music_comparison_questions_draft.tsv")
output_json = Path("outputs/music_comparison_questions_draft.json")

with open(input_file, "r", encoding="utf-8") as f:
    rows = json.load(f)

birth_admin = []
instrument_class = []

for r in rows:
    q = r["question_text"].lower()
    if "administrative territorial entity is the birth place" in q:
        birth_admin.append(r)
    elif "broader instrument class" in q:
        instrument_class.append(r)

comparison_rows = []
seen = set()

def add_question(question_text, answer, path, seeds):
    key = (question_text, answer)
    if key in seen:
        return
    seen.add(key)
    comparison_rows.append({
        "question_id": f"MUSIC_COMP_{len(comparison_rows)+1:03d}",
        "question_text": question_text,
        "gold_answer": answer,
        "reasoning_path": path,
        "seed_entity": " / ".join(seeds),
        "difficulty": "comparison",
        "domain": "Turkish Music"
    })

# 1) Birth-place admin comparisons
for a, b in combinations(birth_admin, 2):
    if a["seed_entity"] == b["seed_entity"]:
        continue
    if a["gold_answer"] == b["gold_answer"]:
        continue

    q1 = f"Which artist was born in {a['gold_answer']}, {a['seed_entity']} or {b['seed_entity']}?"
    add_question(
        q1,
        a["seed_entity"],
        [
            a["seed_entity"], "place of birth", a["reasoning_path"][2],
            "located in the administrative territorial entity", a["gold_answer"]
        ],
        [a["seed_entity"], b["seed_entity"]]
    )

    q2 = f"Which artist was born in {b['gold_answer']}, {a['seed_entity']} or {b['seed_entity']}?"
    add_question(
        q2,
        b["seed_entity"],
        [
            b["seed_entity"], "place of birth", b["reasoning_path"][2],
            "located in the administrative territorial entity", b["gold_answer"]
        ],
        [a["seed_entity"], b["seed_entity"]]
    )

# 2) Instrument-class comparisons
for a, b in combinations(instrument_class, 2):
    if a["seed_entity"] == b["seed_entity"]:
        continue
    if a["gold_answer"] == b["gold_answer"]:
        continue

    q1 = f"Which artist uses an instrument that belongs to the {a['gold_answer']} family, {a['seed_entity']} or {b['seed_entity']}?"
    add_question(
        q1,
        a["seed_entity"],
        [
            a["seed_entity"], "instrument", a["reasoning_path"][2],
            "subclass of", a["gold_answer"]
        ],
        [a["seed_entity"], b["seed_entity"]]
    )

    q2 = f"Which artist uses an instrument that belongs to the {b['gold_answer']} family, {a['seed_entity']} or {b['seed_entity']}?"
    add_question(
        q2,
        b["seed_entity"],
        [
            b["seed_entity"], "instrument", b["reasoning_path"][2],
            "subclass of", b["gold_answer"]
        ],
        [a["seed_entity"], b["seed_entity"]]
    )

# İlk 10'u al, bize 5 lazım; sonra içinden seçeriz
comparison_rows = comparison_rows[:10]

with open(output_tsv, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        "question_id", "question_text", "gold_answer",
        "reasoning_path", "seed_entity", "difficulty", "domain"
    ])
    for r in comparison_rows:
        writer.writerow([
            r["question_id"],
            r["question_text"],
            r["gold_answer"],
            " | ".join(r["reasoning_path"]),
            r["seed_entity"],
            r["difficulty"],
            r["domain"]
        ])

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(comparison_rows, f, ensure_ascii=False, indent=2)

print("Generated comparison questions:", len(comparison_rows))
print("TSV:", output_tsv)
print("JSON:", output_json)

print("\nQuestions:")
for r in comparison_rows:
    print(f"{r['question_id']} | {r['question_text']} -> {r['gold_answer']}")
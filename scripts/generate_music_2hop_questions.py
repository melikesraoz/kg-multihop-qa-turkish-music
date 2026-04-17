from pathlib import Path
import csv
import json

input_file = Path("outputs/music_questionworthy_paths.tsv")
output_tsv = Path("outputs/music_2hop_questions_draft.tsv")
output_json = Path("outputs/music_2hop_questions_draft.json")

# En temiz tuttuğumuz ilişki çiftleri
ALLOWED_PAIRS = {
    ("P19", "P17"),   # place of birth -> country
    ("P19", "P131"),  # place of birth -> located in administrative territorial entity
    ("P1303", "P279"),# instrument -> subclass of
    ("P136", "P31"),  # genre -> instance of
    ("P136", "P279"), # genre -> subclass of
    ("P166", "P31"),  # award received -> instance of
    ("P69", "P17"),   # educated at -> country
    ("P264", "P17"),  # record label -> country
    ("P463", "P495"), # member of -> country of origin
}

# Gürültülü / saçma ontology sonuçlarını ele
BAD_TERMS = [
    "byzantine", "ottoman", "empire", "professions",
    "writter", "auther", "regisseur", "👨", "timothy thompson",
    "politician", "screen-writer", "poetess"
]

def bad_text(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in BAD_TERMS)

def make_question(row):
    r1 = row["r1"]
    r2 = row["r2"]
    seed = row["seed_name"]
    mid = row["mid_name"]

    if (r1, r2) == ("P19", "P17"):
        return f"In which country was {seed} born?"
    if (r1, r2) == ("P19", "P131"):
        return f"In which administrative territorial entity is the birth place of {seed} located?"
    if (r1, r2) == ("P1303", "P279"):
        return f"What broader instrument class does the instrument used by {seed} belong to?"
    if (r1, r2) == ("P136", "P31"):
        return f"What type of music category is the genre associated with {seed}?"
    if (r1, r2) == ("P136", "P279"):
        return f"What broader genre category does the music genre associated with {seed} belong to?"
    if (r1, r2) == ("P166", "P31"):
        return f"What type of award has {seed} received?"
    if (r1, r2) == ("P69", "P17"):
        return f"In which country is the institution where {seed} studied located?"
    if (r1, r2) == ("P264", "P17"):
        return f"In which country is the record label associated with {seed} located?"
    if (r1, r2) == ("P463", "P495"):
        return f"What is the country of origin of the group that {seed} is a member of?"
    return f"What is the relation chain for {seed} via {mid}?"

rows = []
seen_questions = set()

with open(input_file, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        pair = (row["r1"], row["r2"])
        if pair not in ALLOWED_PAIRS:
            continue

        if bad_text(row["mid_name"]) or bad_text(row["end_name"]):
            continue

        question = make_question(row)
        answer = row["end_name"].strip()

        # çok tekrar olmasın
        if question in seen_questions:
            continue
        seen_questions.add(question)

        rows.append({
            "question_id": f"MUSIC_2HOP_{len(rows)+1:03d}",
            "question_text": question,
            "gold_answer": answer,
            "reasoning_path": [
                row["seed_name"], row["r1_name"], row["mid_name"],
                row["r2_name"], row["end_name"]
            ],
            "seed_entity": row["seed_name"],
            "difficulty": "2-hop",
            "domain": "Turkish Music"
        })

# önce daha çeşitli görünmesi için sırayı koruyoruz, sonra ilk 35'i al
rows = rows[:35]

with open(output_tsv, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow([
        "question_id", "question_text", "gold_answer",
        "reasoning_path", "seed_entity", "difficulty", "domain"
    ])
    for r in rows:
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
    json.dump(rows, f, ensure_ascii=False, indent=2)

print("Generated questions:", len(rows))
print("TSV:", output_tsv)
print("JSON:", output_json)

print("\nFirst 15 questions:")
for r in rows[:15]:
    print(f"{r['question_id']} | {r['question_text']} -> {r['gold_answer']}")
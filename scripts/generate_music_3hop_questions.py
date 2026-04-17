from pathlib import Path
from collections import defaultdict
import csv
import json

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
seed_file = Path("data/music_seed_ids.txt")

output_tsv = Path("outputs/music_3hop_questions_draft.tsv")
output_json = Path("outputs/music_3hop_questions_draft.json")

# 3-hop için tutarlı zincirler
ALLOWED_3HOP = {
    ("P19", "P131", "P17"),   # place of birth -> located in admin entity -> country
    ("P1303", "P279", "P279"),# instrument -> subclass -> subclass
    ("P136", "P279", "P279"), # genre -> subclass -> subclass
    ("P166", "P31", "P279"),  # award -> instance -> subclass
    ("P69", "P131", "P17"),   # educated at -> located in admin entity -> country
    ("P264", "P131", "P17"),  # record label -> located in admin entity -> country
}

FIRST_HOP = {x[0] for x in ALLOWED_3HOP}
SECOND_HOP = {x[1] for x in ALLOWED_3HOP}
THIRD_HOP = {x[2] for x in ALLOWED_3HOP}

BAD_TERMS = [
    "byzantine", "ottoman", "empire", "writter", "auther",
    "regisseur", "professions", "greater istanbul", "👨"
]

def bad_text(text: str) -> bool:
    t = text.lower()
    return any(x in t for x in BAD_TERMS)

def load_first_names(path: Path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping

def load_seed_ids(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def make_question(seed, r1, m1, r2, m2, r3, end):
    if (r1, r2, r3) == ("P19", "P131", "P17"):
        return f"In which country is the administrative territorial entity containing the birth place of {seed} located?"
    if (r1, r2, r3) == ("P1303", "P279", "P279"):
        return f"What broader family does the instrument used by {seed} belong to?"
    if (r1, r2, r3) == ("P136", "P279", "P279"):
        return f"What broader musical family does the genre associated with {seed} belong to?"
    if (r1, r2, r3) == ("P166", "P31", "P279"):
        return f"What broader class does an award received by {seed} belong to?"
    if (r1, r2, r3) == ("P69", "P131", "P17"):
        return f"In which country is the administrative territorial entity containing the institution where {seed} studied located?"
    if (r1, r2, r3) == ("P264", "P131", "P17"):
        return f"In which country is the administrative territorial entity containing the record label associated with {seed} located?"
    return f"What is the 3-hop path for {seed}?"

print("Loading names...")
entity_names = load_first_names(entity_file)
relation_names = load_first_names(relation_file)

print("Loading seeds...")
seeds = load_seed_ids(seed_file)
seed_set = set(seeds)

print("Pass 1: seed -> mid1")
seed_to_mid1 = defaultdict(list)
mid1_nodes = set()

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in seed_set and r in FIRST_HOP:
            seed_to_mid1[s].append((r, o))
            mid1_nodes.add(o)

mid1_set = set(mid1_nodes)

print("Pass 2: mid1 -> mid2")
mid1_to_mid2 = defaultdict(list)
mid2_nodes = set()

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in mid1_set and r in SECOND_HOP:
            mid1_to_mid2[s].append((r, o))
            mid2_nodes.add(o)

mid2_set = set(mid2_nodes)

print("Pass 3: mid2 -> end")
mid2_to_end = defaultdict(list)

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in mid2_set and r in THIRD_HOP:
            mid2_to_end[s].append((r, o))

print("Building 3-hop questions...")
rows = []
seen = set()

for seed_id in seeds:
    seed_name = entity_names.get(seed_id, seed_id)

    for r1, m1 in seed_to_mid1.get(seed_id, []):
        for r2, m2 in mid1_to_mid2.get(m1, []):
            for r3, end in mid2_to_end.get(m2, []):
                if (r1, r2, r3) not in ALLOWED_3HOP:
                    continue

                m1_name = entity_names.get(m1, m1)
                m2_name = entity_names.get(m2, m2)
                end_name = entity_names.get(end, end)

                if any(bad_text(x) for x in [m1_name, m2_name, end_name]):
                    continue

                key = (seed_id, r1, m1, r2, m2, r3, end)
                if key in seen:
                    continue
                seen.add(key)

                question = make_question(seed_name, r1, m1_name, r2, m2_name, r3, end_name)

                rows.append({
                    "question_id": f"MUSIC_3HOP_{len(rows)+1:03d}",
                    "question_text": question,
                    "gold_answer": end_name,
                    "reasoning_path": [
                        seed_name,
                        relation_names.get(r1, r1),
                        m1_name,
                        relation_names.get(r2, r2),
                        m2_name,
                        relation_names.get(r3, r3),
                        end_name,
                    ],
                    "seed_entity": seed_name,
                    "difficulty": "3-hop",
                    "domain": "Turkish Music"
                })

# ilk 25'i tut, sonra içinden 15 seçeceğiz
rows = rows[:25]

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

print("Generated 3-hop questions:", len(rows))
print("TSV:", output_tsv)
print("JSON:", output_json)

print("\nFirst 20 questions:")
for r in rows[:20]:
    print(f"{r['question_id']} | {r['question_text']} -> {r['gold_answer']}")
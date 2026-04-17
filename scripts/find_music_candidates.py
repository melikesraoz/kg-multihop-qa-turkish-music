from pathlib import Path
from collections import defaultdict

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
text_file = Path("data/wikidata5m_raw_data/wikidata5m_text.txt")

TURKEY_ID = "Q43"

music_keywords = [
    "singer", "musician", "composer", "songwriter", "rapper",
    "pop star", "record label", "album", "band", "music group",
    "musical group", "rock band", "orchestra", "dj", "vocalist"
]

target_relation_ids = {"P27", "P495", "P17", "P19"}  # citizenship, country of origin, country, place of birth

def load_first_names(path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping

print("Loading names...")
entity_names = load_first_names(entity_file)
relation_names = load_first_names(relation_file)

print("Scanning Q43-connected triples...")
candidate_relations = defaultdict(list)

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        s, r, o = parts
        if r not in target_relation_ids:
            continue

        if o == TURKEY_ID and s != TURKEY_ID:
            candidate_relations[s].append(r)
        elif s == TURKEY_ID and o != TURKEY_ID:
            candidate_relations[o].append(r)

candidate_ids = set(candidate_relations.keys())
print("Candidate IDs connected to Q43 with target relations:", len(candidate_ids))

print("\nFiltering by music-related descriptions...")
music_hits = []

with open(text_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t", 1)
        if len(parts) != 2:
            continue

        qid, desc = parts
        if qid not in candidate_ids:
            continue

        desc_l = desc.lower()
        if any(k in desc_l for k in music_keywords):
            music_hits.append({
                "id": qid,
                "name": entity_names.get(qid, qid),
                "relations": [relation_names.get(x, x) for x in sorted(set(candidate_relations[qid]))],
                "description": desc[:400]
            })

print("\n=== MUSIC CANDIDATES ===")
print("Total music-like candidates:", len(music_hits))

for item in music_hits[:60]:
    print("\nID:", item["id"])
    print("Name:", item["name"])
    print("Relations to Turkey:", item["relations"])
    print("Description:", item["description"])
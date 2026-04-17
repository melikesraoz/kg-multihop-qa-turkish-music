from pathlib import Path
from collections import Counter

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")

target_qid = "Q43"

def load_first_names(path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping

print("Loading entity names...")
entity_names = load_first_names(entity_file)

print("Loading relation names...")
relation_names = load_first_names(relation_file)

connected = []
relation_counter = Counter()

print("Scanning triples connected to Q43...")
with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        s, r, o = parts
        if s == target_qid or o == target_qid:
            connected.append((s, r, o))
            relation_counter[r] += 1

print("\n=== SUMMARY ===")
print("Target entity:", target_qid, "-", entity_names.get(target_qid, "UNKNOWN"))
print("Total connected triples:", len(connected))

print("\n=== TOP RELATIONS (decoded) ===")
for rel_id, cnt in relation_counter.most_common(20):
    rel_name = relation_names.get(rel_id, rel_id)
    print(f"{rel_id} | {rel_name} | {cnt}")

print("\n=== FIRST 50 DECODED TRIPLES ===")
for s, r, o in connected[:50]:
    s_name = entity_names.get(s, s)
    r_name = relation_names.get(r, r)
    o_name = entity_names.get(o, o)
    print(f"({s} | {s_name}) -[{r} | {r_name}]-> ({o} | {o_name})")
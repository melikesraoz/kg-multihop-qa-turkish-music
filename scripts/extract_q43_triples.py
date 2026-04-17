from pathlib import Path
from collections import Counter

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
target_qid = "Q43"

connected = []
relation_counter = Counter()

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        s, r, o = parts
        if s == target_qid or o == target_qid:
            connected.append((s, r, o))
            relation_counter[r] += 1

print("=== Q43 CONNECTED TRIPLES ===")
print("Total connected triples:", len(connected))

print("\nFirst 30 triples:")
for triple in connected[:30]:
    print(triple)

print("\nTop relation IDs:")
for rel, cnt in relation_counter.most_common(20):
    print(rel, cnt)
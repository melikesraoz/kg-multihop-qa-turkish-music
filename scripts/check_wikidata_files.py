from pathlib import Path

base = Path("data")
entity_file = base / "wikidata5m_raw_data" / "wikidata5m_alias" / "wikidata5m_entity.txt"
relation_file = base / "wikidata5m_raw_data" / "wikidata5m_alias" / "wikidata5m_relation.txt"
triplet_file = base / "wikidata5m_raw_data" / "wikidata5m_all_triplet.txt"
kg_file = base / "wikidata5m_kg" / "wikidata5m_kg.jsonl"

files = [entity_file, relation_file, triplet_file, kg_file]

print("=== FILE CHECK ===")
for f in files:
    print(f"{f}: {'OK' if f.exists() else 'MISSING'}")

print("\n=== SAMPLE LINES ===")

if entity_file.exists():
    with open(entity_file, "r", encoding="utf-8") as f:
        print("\nentity sample:")
        for _ in range(3):
            print(f.readline().strip())

if relation_file.exists():
    with open(relation_file, "r", encoding="utf-8") as f:
        print("\nrelation sample:")
        for _ in range(3):
            print(f.readline().strip())

if triplet_file.exists():
    with open(triplet_file, "r", encoding="utf-8") as f:
        print("\ntriplet sample:")
        for _ in range(3):
            print(f.readline().strip())

if kg_file.exists():
    with open(kg_file, "r", encoding="utf-8") as f:
        print("\nkg jsonl sample:")
        for _ in range(2):
            print(f.readline().strip()[:300])
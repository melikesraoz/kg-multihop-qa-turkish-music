import json
from pathlib import Path

kg_file = Path("data/wikidata5m_kg/wikidata5m_kg.jsonl")

keywords = ["turkey", "türkiye", "turkiye", "republic of turkey"]

matches = []

with open(kg_file, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        try:
            obj = json.loads(line)
        except Exception:
            continue

        entity_id = obj.get("entity_id", "")
        desc = (obj.get("entity_description", "") or "").lower()
        aliases = obj.get("entity_alias", []) or []

        alias_text = " ".join(str(a).lower() for a in aliases)

        if any(k in desc or k in alias_text for k in keywords):
            matches.append({
                "entity_id": entity_id,
                "description": obj.get("entity_description", "")[:250],
                "aliases": aliases[:10],
            })

        if len(matches) >= 30:
            break

print("=== TURKIYE / TURKEY CANDIDATES ===")
for m in matches:
    print("\nID:", m["entity_id"])
    print("Description:", m["description"])
    print("Aliases:", m["aliases"])
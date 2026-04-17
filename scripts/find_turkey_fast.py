from pathlib import Path

entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
text_file = Path("data/wikidata5m_raw_data/wikidata5m_text.txt")

exact_targets = {
    "turkey",
    "türkiye",
    "turkiye",
    "republic of turkey",
    "republic of türkiye",
    "republic of turkiye",
}

soft_targets = ["turkey", "türkiye", "turkiye"]

def norm(s: str) -> str:
    return " ".join(s.lower().strip().split())

exact_ids = []
soft_ids = []

print("=== STEP 1: SEARCH IN ENTITY ALIASES ===")

with open(entity_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue

        qid = parts[0]
        aliases_raw = [x for x in parts[1:] if x.strip()]
        aliases = [norm(x) for x in aliases_raw]

        if any(a in exact_targets for a in aliases):
            exact_ids.append((qid, aliases_raw[:10]))
        elif any(any(t in a for t in soft_targets) for a in aliases):
            soft_ids.append((qid, aliases_raw[:10]))

print("\nEXACT MATCHES:")
for qid, aliases in exact_ids[:20]:
    print(qid, "|", aliases)

print("\nSOFT MATCHES:")
for qid, aliases in soft_ids[:20]:
    print(qid, "|", aliases)

candidate_ids = [qid for qid, _ in exact_ids] or [qid for qid, _ in soft_ids[:20]]
candidate_set = set(candidate_ids)

print("\n=== STEP 2: DESCRIPTIONS FROM wikidata5m_text.txt ===")
found = 0

with open(text_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t", 1)
        if len(parts) != 2:
            continue

        qid, desc = parts
        if qid in candidate_set:
            found += 1
            print("\nID:", qid)
            print("Description:", desc[:500])

print("\nDescription matches found:", found)
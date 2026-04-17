from pathlib import Path
from collections import defaultdict

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
seed_file = Path("data/music_seed_ids.txt")
output_file = Path("outputs/music_questionworthy_paths.tsv")

TARGET_RELATIONS = {
    "P19",    # place of birth
    "P106",   # occupation
    "P264",   # record label
    "P136",   # genre
    "P69",    # educated at
    "P166",   # award received
    "P463",   # member of
    "P1303",  # instrument
    "P27",    # country of citizenship
}

SECOND_HOP_RELATIONS = {
    "P17",    # country
    "P31",    # instance of
    "P279",   # subclass of
    "P131",   # located in the administrative territorial entity
    "P361",   # part of
    "P495",   # country of origin
}

GOOD_PAIRS = {
    ("P19", "P17"),
    ("P19", "P131"),
    ("P106", "P31"),
    ("P106", "P279"),
    ("P136", "P31"),
    ("P136", "P279"),
    ("P1303", "P31"),
    ("P1303", "P279"),
    ("P69", "P17"),
    ("P69", "P131"),
    ("P463", "P17"),
    ("P463", "P495"),
    ("P166", "P17"),
    ("P166", "P31"),
    ("P264", "P17"),
    ("P264", "P131"),
}

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

def template_hint(r1, r2, seed_name, mid_name, end_name):
    if (r1, r2) == ("P19", "P17"):
        return f"What is the country of birth place of {seed_name}?"
    if (r1, r2) == ("P19", "P131"):
        return f"In which administrative area is the birth place of {seed_name} located?"
    if (r1, r2) == ("P106", "P279"):
        return f"What broader occupational class does {seed_name}'s occupation belong to?"
    if (r1, r2) == ("P136", "P279"):
        return f"What broader genre category does {seed_name}'s music genre belong to?"
    if (r1, r2) == ("P1303", "P279"):
        return f"What broader instrument class does the instrument of {seed_name} belong to?"
    if (r1, r2) == ("P69", "P17"):
        return f"In which country is the institution where {seed_name} studied located?"
    if (r1, r2) == ("P463", "P495"):
        return f"What is the country of origin of the group that {seed_name} is a member of?"
    if (r1, r2) == ("P166", "P31"):
        return f"What type of award has {seed_name} received?"
    if (r1, r2) == ("P264", "P17"):
        return f"In which country is the record label of {seed_name} located?"
    return f"{seed_name} --[{r1}]--> {mid_name} --[{r2}]--> {end_name}"

print("Loading names...")
entity_names = load_first_names(entity_file)
relation_names = load_first_names(relation_file)

print("Loading seeds...")
seeds = load_seed_ids(seed_file)
seed_set = set(seeds)

print("Pass 1: collecting seed -> mid edges...")
seed_to_mid = defaultdict(list)
mid_nodes = set()

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in seed_set and r in TARGET_RELATIONS:
            seed_to_mid[s].append((r, o))
            mid_nodes.add(o)

mid_set = set(mid_nodes)

print("Pass 2: collecting mid -> end edges...")
mid_to_end = defaultdict(list)

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in mid_set and r in SECOND_HOP_RELATIONS:
            mid_to_end[s].append((r, o))

print("Filtering question-worthy paths...")
rows = []
seen = set()

for seed in seeds:
    seed_name = entity_names.get(seed, seed)

    for r1, mid in seed_to_mid.get(seed, []):
        for r2, end in mid_to_end.get(mid, []):
            if (r1, r2) not in GOOD_PAIRS:
                continue
            if end == seed:
                continue

            key = (seed, r1, mid, r2, end)
            if key in seen:
                continue
            seen.add(key)

            mid_name = entity_names.get(mid, mid)
            end_name = entity_names.get(end, end)

            rows.append({
                "seed_id": seed,
                "seed_name": seed_name,
                "r1": r1,
                "r1_name": relation_names.get(r1, r1),
                "mid": mid,
                "mid_name": mid_name,
                "r2": r2,
                "r2_name": relation_names.get(r2, r2),
                "end": end,
                "end_name": end_name,
                "template_hint": template_hint(r1, r2, seed_name, mid_name, end_name),
            })

print("Total filtered paths:", len(rows))

with open(output_file, "w", encoding="utf-8") as f:
    f.write("seed_id\tseed_name\tr1\tr1_name\tmid\tmid_name\tr2\tr2_name\tend\tend_name\ttemplate_hint\n")
    for row in rows:
        f.write(
            f"{row['seed_id']}\t{row['seed_name']}\t"
            f"{row['r1']}\t{row['r1_name']}\t"
            f"{row['mid']}\t{row['mid_name']}\t"
            f"{row['r2']}\t{row['r2_name']}\t"
            f"{row['end']}\t{row['end_name']}\t"
            f"{row['template_hint']}\n"
        )

print(f"Saved to: {output_file}")

print("\nFirst 30 filtered paths:")
for row in rows[:30]:
    print(
        f"{row['seed_name']} --[{row['r1_name']}]--> {row['mid_name']} "
        f"--[{row['r2_name']}]--> {row['end_name']}"
    )
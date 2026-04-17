from pathlib import Path
from collections import defaultdict

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
seed_file = Path("data/music_seed_ids.txt")
output_file = Path("outputs/music_reasoning_paths.txt")

# Music-relevant 1-hop relations we care about
TARGET_RELATIONS = {
    "P19",    # place of birth
    "P20",    # place of death
    "P106",   # occupation
    "P264",   # record label
    "P136",   # genre
    "P1412",  # languages spoken/written/signed
    "P69",    # educated at
    "P166",   # award received
    "P463",   # member of
    "P1303",  # instrument
    "P27",    # country of citizenship
}

# Good 2nd-hop relations to continue from the middle node
SECOND_HOP_RELATIONS = {
    "P17",    # country
    "P31",    # instance of
    "P279",   # subclass of
    "P131",   # located in administrative territorial entity
    "P361",   # part of
    "P527",   # has part(s)
    "P495",   # country of origin
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

print("Building reasoning paths...")
all_paths = []

for seed in seeds:
    seed_name = entity_names.get(seed, seed)

    for r1, mid in seed_to_mid.get(seed, []):
        mid_name = entity_names.get(mid, mid)
        r1_name = relation_names.get(r1, r1)

        for r2, end in mid_to_end.get(mid, []):
            end_name = entity_names.get(end, end)
            r2_name = relation_names.get(r2, r2)

            # skip useless loops
            if end == seed:
                continue

            all_paths.append({
                "seed_id": seed,
                "seed_name": seed_name,
                "r1": r1,
                "r1_name": r1_name,
                "mid": mid,
                "mid_name": mid_name,
                "r2": r2,
                "r2_name": r2_name,
                "end": end,
                "end_name": end_name,
            })

# remove duplicate paths
unique = []
seen = set()

for p in all_paths:
    key = (p["seed_id"], p["r1"], p["mid"], p["r2"], p["end"])
    if key not in seen:
        seen.add(key)
        unique.append(p)

print("\n=== SUMMARY ===")
print("Total raw paths:", len(all_paths))
print("Total unique paths:", len(unique))

# group by seed
by_seed = defaultdict(list)
for p in unique:
    by_seed[p["seed_id"]].append(p)

lines = []
for seed in seeds:
    seed_name = entity_names.get(seed, seed)
    paths = by_seed.get(seed, [])

    print(f"{seed} | {seed_name} | unique 2-hop paths = {len(paths)}")

    lines.append("=" * 80)
    lines.append(f"SEED: {seed} | {seed_name}")
    lines.append(f"UNIQUE 2-HOP PATH COUNT: {len(paths)}")

    for p in paths[:25]:
        lines.append(
            f"{p['seed_name']} --[{p['r1_name']}]--> {p['mid_name']} "
            f"--[{p['r2_name']}]--> {p['end_name']}"
        )

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"\nDetailed paths saved to: {output_file}")
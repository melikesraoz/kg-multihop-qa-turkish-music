from pathlib import Path
import csv
import re

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
text_file = Path("data/wikidata5m_raw_data/wikidata5m_text.txt")
seed_file = Path("data/music_seed_ids.txt")

nodes_out = Path("outputs/music_subset_small_nodes.csv")
rels_out = Path("outputs/music_subset_small_relationships.csv")

FIRST_HOP = {
    "P19",   # place of birth
    "P106",  # occupation
    "P264",  # record label
    "P136",  # genre
    "P69",   # educated at
    "P166",  # award received
    "P463",  # member of
    "P1303", # instrument
    "P27",   # country of citizenship
}

SECOND_HOP = {
    "P17",   # country
    "P131",  # located in admin territorial entity
    "P31",   # instance of
    "P279",  # subclass of
    "P495",  # country of origin
}

THIRD_HOP = {
    "P17",
    "P31",
    "P279",
}

def load_first_names(path: Path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping

def load_descriptions(path: Path):
    mapping = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) == 2:
                mapping[parts[0]] = parts[1]
    return mapping

def load_seed_ids(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def sanitize_rel_type(name: str, rel_id: str) -> str:
    if not name:
        return f"REL_{rel_id}"
    t = name.upper()
    t = re.sub(r"[^A-Z0-9]+", "_", t)
    t = re.sub(r"_+", "_", t).strip("_")
    if not t:
        t = f"REL_{rel_id}"
    if t[0].isdigit():
        t = f"REL_{t}"
    return t

print("Loading metadata...")
entity_names = load_first_names(entity_file)
relation_names = load_first_names(relation_file)
descriptions = load_descriptions(text_file)
seeds = load_seed_ids(seed_file)
seed_set = set(seeds)

triples = set()
all_nodes = set(seed_set)

mid1_nodes = set()
mid2_nodes = set()

print("Pass 1: seed -> mid1")
with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in seed_set and r in FIRST_HOP:
            triples.add((s, r, o))
            all_nodes.update([s, o])
            mid1_nodes.add(o)

mid1_set = set(mid1_nodes)

print("Pass 2: mid1 -> mid2")
with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in mid1_set and r in SECOND_HOP:
            triples.add((s, r, o))
            all_nodes.update([s, o])
            mid2_nodes.add(o)

mid2_set = set(mid2_nodes)

print("Pass 3: mid2 -> end")
with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in mid2_set and r in THIRD_HOP:
            triples.add((s, r, o))
            all_nodes.update([s, o])

print("Writing nodes...")
with open(nodes_out, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["entityId", "name", "description"])
    for qid in sorted(all_nodes):
        writer.writerow([
            qid,
            entity_names.get(qid, qid),
            descriptions.get(qid, "")
        ])

print("Writing relationships...")
with open(rels_out, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["start_id", "end_id", "relation_id", "relation_name", "rel_type"])
    for s, r, o in sorted(triples):
        rel_name = relation_names.get(r, r)
        rel_type = sanitize_rel_type(rel_name, r)
        writer.writerow([s, o, r, rel_name, rel_type])

print("Done.")
print("Nodes:", len(all_nodes))
print("Relationships:", len(triples))
print("Nodes CSV:", nodes_out)
print("Relationships CSV:", rels_out)
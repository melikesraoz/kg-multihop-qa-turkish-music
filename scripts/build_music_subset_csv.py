from pathlib import Path
import csv
import re

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
text_file = Path("data/wikidata5m_raw_data/wikidata5m_text.txt")
seed_file = Path("data/music_seed_ids.txt")

nodes_out = Path("outputs/music_subset_nodes.csv")
rels_out = Path("outputs/music_subset_relationships.csv")

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

print("Pass 1: seed 1-hop...")
triples = set()
first_ring = set()
all_nodes = set(seed_set)

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in seed_set or o in seed_set:
            triples.add((s, r, o))
            all_nodes.update([s, o])
            if s not in seed_set:
                first_ring.add(s)
            if o not in seed_set:
                first_ring.add(o)

print("Pass 2: neighbors of first-ring...")
with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue
        s, r, o = parts
        if s in first_ring or o in first_ring:
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
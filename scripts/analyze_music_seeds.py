from pathlib import Path
from collections import defaultdict, Counter

triplet_file = Path("data/wikidata5m_raw_data/wikidata5m_all_triplet.txt")
entity_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_entity.txt")
relation_file = Path("data/wikidata5m_raw_data/wikidata5m_alias/wikidata5m_relation.txt")
seed_file = Path("data/music_seed_ids.txt")
output_file = Path("outputs/music_seed_analysis.txt")


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

print("Loading seed IDs...")
seeds = load_seed_ids(seed_file)
seed_set = set(seeds)

print("Pass 1: collecting 1-hop neighbors...")
seed_edges = defaultdict(list)
mid_nodes = set()

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        s, r, o = parts

        if s in seed_set:
            seed_edges[s].append(("out", r, o))
            mid_nodes.add(o)

        if o in seed_set:
            seed_edges[o].append(("in", r, s))
            mid_nodes.add(s)

mid_set = set(mid_nodes)

print("Pass 2: collecting edges around 1-hop mids...")
mid_edges = defaultdict(list)

with open(triplet_file, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) != 3:
            continue

        s, r, o = parts

        if s in mid_set:
            mid_edges[s].append(("out", r, o))
        if o in mid_set:
            mid_edges[o].append(("in", r, s))

print("Analyzing seeds...")
lines = []
summary = []

for seed in seeds:
    onehop = seed_edges.get(seed, [])
    onehop_neighbors = {nbr for _, _, nbr in onehop}
    onehop_relations = Counter(r for _, r, _ in onehop)

    twohop_paths = set()

    for dir1, r1, mid in onehop:
        for dir2, r2, end in mid_edges.get(mid, []):
            if end == seed:
                continue
            twohop_paths.add((mid, r1, r2, end))

    seed_name = entity_names.get(seed, seed)

    summary.append({
        "seed_id": seed,
        "seed_name": seed_name,
        "onehop_edge_count": len(onehop),
        "onehop_neighbor_count": len(onehop_neighbors),
        "relation_type_count": len(onehop_relations),
        "twohop_path_count": len(twohop_paths),
        "top_relations": onehop_relations.most_common(8),
        "sample_paths": list(twohop_paths)[:8],
    })

summary.sort(key=lambda x: x["twohop_path_count"], reverse=True)

for item in summary:
    lines.append("=" * 80)
    lines.append(f"SEED: {item['seed_id']} | {item['seed_name']}")
    lines.append(f"1-hop edges: {item['onehop_edge_count']}")
    lines.append(f"1-hop unique neighbors: {item['onehop_neighbor_count']}")
    lines.append(f"1-hop relation types: {item['relation_type_count']}")
    lines.append(f"2-hop candidate paths: {item['twohop_path_count']}")
    lines.append("Top relations:")
    for rel_id, cnt in item["top_relations"]:
        rel_name = relation_names.get(rel_id, rel_id)
        lines.append(f"  {rel_id} | {rel_name} | {cnt}")

    lines.append("Sample 2-hop paths:")
    for mid, r1, r2, end in item["sample_paths"]:
        mid_name = entity_names.get(mid, mid)
        end_name = entity_names.get(end, end)
        r1_name = relation_names.get(r1, r1)
        r2_name = relation_names.get(r2, r2)
        lines.append(
            f"  {item['seed_name']} --[{r1_name}]--> {mid_name} --[{r2_name}]--> {end_name}"
        )

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("\n=== TOP 15 SEEDS BY 2-HOP PATH COUNT ===")
for item in summary[:15]:
    print(
        f"{item['seed_id']} | {item['seed_name']} | "
        f"1-hop neighbors={item['onehop_neighbor_count']} | "
        f"relation types={item['relation_type_count']} | "
        f"2-hop paths={item['twohop_path_count']}"
    )

print(f"\nDetailed report saved to: {output_file}")
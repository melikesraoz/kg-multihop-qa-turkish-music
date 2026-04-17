from pathlib import Path
from neo4j import GraphDatabase
import json
from config import NEO4J_URI as URI, NEO4J_USER as USER, NEO4J_PASSWORD as PASSWORD

# Demo sorusu
QUERY = "In which country was Zulfu Livaneli born?"
SEED_HINT = "Zulfu Livaneli"

MAX_ROUNDS = 2
MAX_TRIPLES_PER_ROUND = 10

OUTPUT_JSON = Path("outputs/spreading_activation_demo.json")
OUTPUT_TXT = Path("outputs/spreading_activation_demo.txt")


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def relation_priority(query: str):
    q = normalize(query)

    if "born" in q or "birth" in q:
        return {
            "place of birth",
            "country",
            "located in the administrative territorial entity",
        }

    if "instrument" in q:
        return {
            "instrument",
            "subclass of",
            "instance of",
        }

    if "genre" in q:
        return {
            "genre",
            "subclass of",
            "instance of",
        }

    if "award" in q:
        return {
            "award received",
            "instance of",
            "subclass of",
        }

    if "record label" in q:
        return {
            "record label",
            "country",
            "located in the administrative territorial entity",
        }

    return set()


driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def find_seed_entity(session, hint: str):
    result = session.run(
        """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($hint)
        RETURN e.entityId AS id, e.name AS name, e.description AS description
        LIMIT 5
        """,
        hint=hint,
    )
    return [dict(r) for r in result]


def get_outgoing_triples(session, entity_id: str):
    result = session.run(
        """
        MATCH (e:Entity {entityId: $entity_id})-[r]->(n:Entity)
        RETURN
            e.entityId AS source_id,
            e.name AS source_name,
            r.relationId AS relation_id,
            r.relationName AS relation_name,
            type(r) AS relation_type,
            n.entityId AS target_id,
            n.name AS target_name
        """,
        entity_id=entity_id,
    )
    return [dict(r) for r in result]


def select_relevant_triples(triples, query: str, visited_entities: set, max_k: int):
    preferred = relation_priority(query)

    scored = []
    for t in triples:
        rel_name = normalize(t.get("relation_name", ""))

        score = 0
        if rel_name in preferred:
            score += 10

        if "country" in rel_name:
            score += 3
        if "birth" in rel_name:
            score += 3
        if "located in the administrative territorial entity" in rel_name:
            score += 2
        if "instrument" in rel_name:
            score += 2
        if "genre" in rel_name:
            score += 2
        if "award" in rel_name:
            score += 2

        scored.append((score, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [t for score, t in scored[:max_k]]

    if not selected:
        selected = triples[:max_k]

    return selected


with driver.session() as session:
    seed_candidates = find_seed_entity(session, SEED_HINT)

    if not seed_candidates:
        print("No seed candidate found.")
        driver.close()
        raise SystemExit

    seed = seed_candidates[0]
    print("Selected seed:")
    print(seed["id"], "|", seed["name"])

    current_entities = [seed["id"]]
    visited_entities = {seed["id"]}
    activation_memory = []

    for round_idx in range(1, MAX_ROUNDS + 1):
        print(f"\n=== ROUND {round_idx} ===")
        next_entities = []

        for entity_id in current_entities:
            triples = get_outgoing_triples(session, entity_id)
            selected = select_relevant_triples(
                triples, QUERY, visited_entities, MAX_TRIPLES_PER_ROUND
            )

            for t in selected:
                activation_memory.append({
                    "round": round_idx,
                    **t
                })
                print(
                    f"{t['source_name']} --[{t['relation_name']}]--> {t['target_name']}"
                )

                if t["target_id"] not in visited_entities:
                    visited_entities.add(t["target_id"])
                    next_entities.append(t["target_id"])

        if not next_entities:
            print("No new entities to activate.")
            break

        current_entities = next_entities

summary_lines = []
summary_lines.append(f"Query: {QUERY}")
summary_lines.append(f"Seed: {seed['name']} ({seed['id']})")
summary_lines.append("")

for item in activation_memory:
    summary_lines.append(
        f"Round {item['round']}: "
        f"{item['source_name']} --[{item['relation_name']}]--> {item['target_name']}"
    )

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump(
        {
            "query": QUERY,
            "seed": seed,
            "visited_entities": list(visited_entities),
            "triples": activation_memory,
        },
        f,
        ensure_ascii=False,
        indent=2,
    )

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    f.write("\n".join(summary_lines))

print("\nSaved:")
print(OUTPUT_JSON)
print(OUTPUT_TXT)

driver.close()
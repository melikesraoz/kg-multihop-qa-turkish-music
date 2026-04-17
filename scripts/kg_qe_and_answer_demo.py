from pathlib import Path
from neo4j import GraphDatabase
import json
from config import NEO4J_URI as URI, NEO4J_USER as USER, NEO4J_PASSWORD as PASSWORD

activation_file = Path("outputs/spreading_activation_demo.json")
output_json = Path("outputs/kg_qe_and_answer_demo.json")
output_txt = Path("outputs/kg_qe_and_answer_demo.txt")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


def get_entity_description(session, entity_id: str):
    result = session.run(
        """
        MATCH (e:Entity {entityId: $id})
        RETURN e.description AS description
        """,
        id=entity_id,
    ).single()
    return result["description"] if result and result["description"] else ""


def build_kg_summary(query, triples):
    # Soruya göre daha anlamlı özet
    rel_map = {}
    for t in triples:
        rel_map.setdefault(t["relation_name"], []).append(t)

    lines = []

    if "place of birth" in rel_map:
        t = rel_map["place of birth"][0]
        lines.append(f"{t['source_name']} was born in {t['target_name']}.")

    if "located in the administrative territorial entity" in rel_map:
        t = rel_map["located in the administrative territorial entity"][0]
        lines.append(f"{t['source_name']} is located in {t['target_name']}.")

    if "country" in rel_map:
        # ilk uygun country relation
        t = rel_map["country"][0]
        lines.append(f"{t['source_name']} is in {t['target_name']}.")

    if "country of citizenship" in rel_map:
        t = rel_map["country of citizenship"][0]
        lines.append(f"{t['source_name']} has citizenship in {t['target_name']}.")

    if not lines:
        # fallback
        for t in triples[:5]:
            lines.append(f"{t['source_name']} {t['relation_name']} {t['target_name']}.")

    return " ".join(lines)


def build_expanded_query(original_query, triples):
    seed_name = triples[0]["source_name"] if triples else "the entity"

    # query simplification mantığı
    for t in triples:
        if t["relation_name"] == "place of birth":
            return f"What is the birthplace of {seed_name}?"
    for t in triples:
        if t["relation_name"] == "country of citizenship":
            return f"What country is {seed_name} associated with?"
    return f"What information is relevant to answering: {original_query}"


def build_passage_note(seed_name, seed_description):
    if not seed_description:
        return f"{seed_name} is a Turkish music-related entity."
    return seed_description[:500]


def build_enhanced_note(passage_note, kg_summary):
    return f"{passage_note}\n\nKnowledge graph facts: {kg_summary}"


def answer_from_kg(query, triples):
    q = query.lower()

    # Doğrudan KG cevabı
    if "country" in q and "born" in q:
        birthplace = None
        country = None

        for t in triples:
            if t["relation_name"] == "place of birth":
                birthplace = t["target_name"]

        if birthplace:
            for t in triples:
                if t["source_name"] == birthplace and t["relation_name"] == "country":
                    country = t["target_name"]
                    break

        if country:
            return country

    # fallback
    for t in triples:
        if t["relation_name"] == "country":
            return t["target_name"]

    return "No confident answer found."


with open(activation_file, "r", encoding="utf-8") as f:
    activation = json.load(f)

query = activation["query"]
seed = activation["seed"]
triples = activation["triples"]

with driver.session() as session:
    seed_description = get_entity_description(session, seed["id"])

kg_summary = build_kg_summary(query, triples)
expanded_query = build_expanded_query(query, triples)
passage_note = build_passage_note(seed["name"], seed_description)
enhanced_note = build_enhanced_note(passage_note, kg_summary)
final_answer = answer_from_kg(query, triples)

result = {
    "query": query,
    "seed": seed,
    "kg_summary": kg_summary,
    "expanded_query": expanded_query,
    "passage_note": passage_note,
    "enhanced_note": enhanced_note,
    "final_answer": final_answer
}

with open(output_json, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

with open(output_txt, "w", encoding="utf-8") as f:
    f.write(f"Original Query: {query}\n\n")
    f.write(f"Seed: {seed['name']} ({seed['id']})\n\n")
    f.write(f"KG Summary:\n{kg_summary}\n\n")
    f.write(f"Expanded Query:\n{expanded_query}\n\n")
    f.write(f"Passage Note:\n{passage_note}\n\n")
    f.write(f"Enhanced Note:\n{enhanced_note}\n\n")
    f.write(f"Final Answer:\n{final_answer}\n")

print("KG Summary:", kg_summary)
print("Expanded Query:", expanded_query)
print("Final Answer:", final_answer)
print("Saved:", output_json)
print("Saved:", output_txt)

driver.close()
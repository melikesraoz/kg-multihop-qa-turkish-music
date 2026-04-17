from pathlib import Path
from neo4j import GraphDatabase
import csv
from collections import defaultdict
from config import NEO4J_URI as URI, NEO4J_USER as USER, NEO4J_PASSWORD as PASSWORD

nodes_file = Path("outputs/music_subset_small_nodes.csv")
rels_file = Path("outputs/music_subset_small_relationships.csv")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

with driver.session() as session:
    print("Creating constraints/indexes...")
    session.run("CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.entityId IS UNIQUE")
    session.run("CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)")

    print("Reading nodes...")
    nodes = []
    with open(nodes_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            nodes.append(row)

    print("Importing nodes...")
    for batch in chunked(nodes, 1000):
        session.run("""
        UNWIND $rows AS row
        MERGE (e:Entity {entityId: row.entityId})
        SET e.name = row.name,
            e.description = row.description
        """, rows=batch)

    print("Reading relationships...")
    rel_groups = defaultdict(list)
    with open(rels_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rel_groups[row["rel_type"]].append(row)

    print("Importing relationships...")
    for rel_type, rows in rel_groups.items():
        query = f"""
        UNWIND $rows AS row
        MATCH (s:Entity {{entityId: row.start_id}})
        MATCH (o:Entity {{entityId: row.end_id}})
        MERGE (s)-[r:{rel_type} {{relationId: row.relation_id}}]->(o)
        SET r.relationName = row.relation_name
        """
        for batch in chunked(rows, 1000):
            session.run(query, rows=batch)

    node_count = session.run("MATCH (n:Entity) RETURN count(n) AS c").single()["c"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]

    print("Import complete.")
    print("Neo4j node count:", node_count)
    print("Neo4j relationship count:", rel_count)

driver.close()
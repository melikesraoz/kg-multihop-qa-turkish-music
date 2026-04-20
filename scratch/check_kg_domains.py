import json
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

def check_domains():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    domains = {
        "Football": "football",
        "Cinema": "director",
        "Companies": "airline",
        "Academia": "university"
    }
    
    counts = {}
    
    with driver.session(database=NEO4J_DATABASE) as session:
        for domain, keyword in domains.items():
            query = f"MATCH (e:Entity) WHERE e.description CONTAINS '{keyword}' RETURN count(e) AS c"
            res = session.run(query).single()
            counts[domain] = res["c"]
            
    print(json.dumps(counts, indent=2))
    driver.close()

if __name__ == "__main__":
    check_domains()

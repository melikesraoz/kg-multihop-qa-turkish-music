"""
module1_spreading_activation.py - KG-Guided Spreading Activation

Bu modul, seed entity'lerden baslayarak Neo4j uzerinde komsulari bulur
ve LLM kullanarak en alakali iliskileri secip genisletir.
"""
from typing import List, Dict, Set
from neo4j import GraphDatabase
from llm_client import ask_llm

def find_seed(session, query: str):
    """
    Sorguya en uygun baslangic entity'sini (seed) bulur.
    Akilli sekilde LLM kullanarak sorudan entity'i ceker ve B-Tree index uzerinden arar.
    """
    try:
        prompt = f"Extract the main named entity (person, band, album, etc.) from this question: '{query}'. Reply with ONLY the entity name, nothing else."
        entity_name = ask_llm(prompt).strip(" \n'\".,")
        print(f"[LLM Entity Extraction] Bulunan Entity Adayi: {entity_name}")
        
        # 1. Tam Eşleşme (Çok Hızlı)
        res = session.run("MATCH (e:Entity) WHERE toLower(e.name) = toLower($n) RETURN e LIMIT 1", n=entity_name).single()
        if res:
            node = res["e"]
            return {"entity_id": node["entityId"], "name": node["name"]}
            
        # 2. Kısmi Eşleşme (Contains)
        res_contains = session.run("MATCH (e:Entity) WHERE toLower(e.name) CONTAINS toLower($n) RETURN e LIMIT 1", n=entity_name).single()
        if res_contains:
            node = res_contains["e"]
            return {"entity_id": node["entityId"], "name": node["name"]}
            
    except Exception as e:
        print(f"Warning: LLM Entity Extraction failed ({e})")
        pass
         
    # Yedek plan: isimlerde CONTAINS ile ara
    words = query.replace("?", "").replace(".", "").split()
    for w in sorted(words, key=len, reverse=True):
        if len(w) > 4:
            res_contains = session.run("""
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($w)
            RETURN e.entityId AS entityId, e.name AS name, e.description AS description
            LIMIT 1
            """, w=w).single()
            if res_contains:
                return {"entity_id": res_contains["entityId"], "name": res_contains["name"], "score": -1}
    return None

def fetch_one_hop_neighbors(session, entity_ids: List[str]) -> List[Dict]:
    """Verilen entity'lerin 1-hop komsularini getirir."""
    cypher = """
    UNWIND $eids AS eid
    MATCH (s:Entity {entityId: eid})-[r]->(h:Entity)
    RETURN s.entityId AS source_id, 
           s.name AS source_name, 
           type(r) AS relation_name, 
           h.entityId AS target_id, 
           h.name AS target_name
    """
    results = []
    for record in session.run(cypher, eids=entity_ids):
        results.append({
            "source_id": record["source_id"],
            "source_name": record["source_name"],
            "relation_name": record["relation_name"],
            "target_id": record["target_id"],
            "target_name": record["target_name"]
        })
    return results

def select_triples_with_llm(query: str, triples: List[Dict]) -> List[Dict]:
    """LLM kullanarak sorguya yardimci olabilecek triple'lari secer."""
    if not triples:
        return []
        
    triple_text = "\n".join(
        f"{i+1}. {t['source_name']} --[{t['relation_name']}]--> {t['target_name']}"
        for i, t in enumerate(triples)
    )

    prompt = f"""Given the question: "{query}"

Below are facts (triples) from a knowledge graph.
Select the triple numbers that are RELEVANT or COULD LEAD to answering the question.
If multiple facts seem useful, try to pick the most direct ones.

Triples:
{triple_text}

Reply with ONLY the numbers separated by commas. Example: 1, 4, 7
If none are relevant, reply with ONLY: 0
"""
    try:
        response = ask_llm(prompt)
        selected_indices = []
        for part in response.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(triples):
                    selected_indices.append(idx)
        return [triples[i] for i in selected_indices]
    except Exception as e:
        print(f"Warning: LLM selection failed ({e}). Returning first 3 triples as fallback.")
        return triples[:3]

def summarize_subgraph(query: str, collected_triples: List[Dict]) -> str:
    """Toplanan graf parcasini LLM ile parca olarak ozetler."""
    if not collected_triples:
        return "No relevant graph facts found."
        
    triple_text = "\n".join(
        f"- {t['source_name']} is related via '{t['relation_name']}' to {t['target_name']}"
        for t in collected_triples
    )

    prompt = f"""Given these facts extracted from a knowledge graph:
{triple_text}

Write a brief, concise natural language summary of the key facts relevant to answering the following question:
"{query}"

Keep the summary coherent and fact-based. Only use the facts provided above.
"""
    try:
        return ask_llm(prompt)
    except Exception as e:
        print(f"Warning: Subgraph summarization failed ({e}). Returning raw facts.")
        return triple_text

def spreading_activation(session, query: str, initial_seed: Dict, max_rounds=2) -> List[Dict]:
    """LLM yonlendirmeli Spreading Activation algoritmasi."""
    all_collected_triples = []
    
    current_entities = [initial_seed["entity_id"]]
    visited_entities = set(current_entities)
    
    for rnd in range(max_rounds):
        print(f"\n--- Spreading Activation Round {rnd+1} ---")
        
        # 1-hop komsulari al
        triples = fetch_one_hop_neighbors(session, current_entities)
        
        # Ziyaret edilmis hedefleri filtrele (donguyu onlemek icin)
        triples = [t for t in triples if t["target_id"] not in visited_entities]
        print(f"Bulan yeni aday triple sayisi: {len(triples)}")
        
        if not triples:
            print("Genisletilecek yeni komsu kalmadi.")
            break
            
        # Pahaliligi onlemek icin adaylari buda (ornegin maks 30)
        # Pratik amacli eger bir seed cok baglantiliysa ilk 30'u alalim
        # Gercek projede heuristic on-eleme yapilir (bm25 vb)
        candidate_triples = triples[:30] 
            
        # LLM ile sececegiz
        selected = select_triples_with_llm(query, candidate_triples)
        print(f"LLM {len(selected)} adet triple secti.")
        
        if not selected:
            break
            
        all_collected_triples.extend(selected)
        
        # Yeni seed'leri belirle
        current_entities = []
        for t in selected:
            if t["target_id"] not in visited_entities:
                current_entities.append(t["target_id"])
                visited_entities.add(t["target_id"])
                
        if not current_entities:
            break

    return all_collected_triples

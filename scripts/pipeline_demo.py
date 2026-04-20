"""
pipeline_demo.py - Pure GraphRAG Pipeline

Neo4j uzerinden 3 adimli tam KG-RAG mimarisini (metinsiz) calistirir.
"""
import sys
import json
from neo4j import GraphDatabase

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

# Modulleri yukle
from module1_spreading_activation import find_seed, spreading_activation, summarize_subgraph
from module2_query_expansion import expand_query
from module3_answer_generation import generate_answer

def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

def main(question: str):
    print_header(f"QUESTION: {question}")
    
    # 0. Altyapiyi hazirla
    print("\n[Init] Sadece Neo4j Veritabanina Baglaniliyor... (Corpus YOK)")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    kg_summary = ""
    seed_name = None
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            # 1. Spreading Activation
            print_header("Module 1: KG Spreading Activation")
            seed_name = find_seed(session, question)
            if not seed_name:
                print("HATA: Soru ile eslesen bir seed entity bulunamadi.")
                kg_summary = "No entities found in knowledge graph."
            else:
                print(f"Seed Bulundu: {seed_name}")
                triples = spreading_activation(session, question, seed_name, max_rounds=2)
                
                print(f"\nToplanan triple sayisi: {len(triples)}")
                for t in triples:
                    print(f"  - {t['source_name']} -> {t['relation_name']} -> {t['target_name']}")
                    
                kg_summary = summarize_subgraph(question, triples)
                print(f"\nKG Summary:\n{kg_summary}")

    except Exception as e:
         print(f"Neo4j Hata: {e}")
         kg_summary = "Knowledge graph could not be accessed."
    finally:
         driver.close()

    # 2. Query Contextualization (Graph-Based)       
    print_header("Module 2: Graph-Augmented Query Formulation")
    expanded = expand_query(question, kg_summary)
    print(f"Original Query: {question}")
    print(f"Graph-Augmented Query: {expanded}")
    
    # 3. Answer Generation
    print_header("Module 3: Pure Graph Answer Generation")
    print("Groq'a Graf verisi gönderiliyor...")
    answer = generate_answer(expanded, kg_summary)
    
    print_header(f"FINAL ANSWER:\n\n{answer}")
    
    # Rapor Ciktisi
    result = {
        "question": question,
        "seed_entity": seed_name,
        "module1_kg_summary": kg_summary,
        "module2_augmented_query": expanded,
        "final_answer": answer
    }
    
    with open("outputs/pipeline_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\nResult saved to: outputs/pipeline_result.json")

if __name__ == "__main__":
    q = "In which country was Zulfu Livaneli born?"
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    main(q)

import json
import csv
import time
from pathlib import Path
from neo4j import GraphDatabase

from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
from llm_client import ask_llm
from metrics import calculate_exact_match, calculate_f1

# RAG Modules
from module1_spreading_activation import find_seed, spreading_activation, summarize_subgraph
from module2_query_expansion import expand_query
from module3_answer_generation import generate_answer

def run_nor(question: str) -> str:
    """1. NoR (No Retrieval) - Just raw LLM knowledge"""
    prompt = f"Question: {question}\nProvide ONLY the answer. Do not add conversational filler. Be as precise as possible.\nAnswer:"
    return ask_llm(prompt)

def run_graph_rag_1hop(session, question: str) -> str:
    """2. 1-Hop Graph RAG - Only direct neighbors"""
    seed_name = find_seed(session, question)
    if not seed_name:
        kg_summary = "No entities found in knowledge graph."
        expanded = question
    else:
        triples = spreading_activation(session, question, seed_name, max_rounds=1)
        kg_summary = summarize_subgraph(question, triples)
        expanded = expand_query(question, kg_summary)
        
    return generate_answer(expanded, kg_summary)

def run_graph_rag_2hop(session, question: str) -> str:
    """3. 2-Hop Graph RAG - Full depth graph logic"""
    seed_name = find_seed(session, question)
    if not seed_name:
        kg_summary = "No entities found in knowledge graph."
        expanded = question
    else:
        triples = spreading_activation(session, question, seed_name, max_rounds=2)
        kg_summary = summarize_subgraph(question, triples)
        expanded = expand_query(question, kg_summary)
        
    return generate_answer(expanded, kg_summary)

def evaluate():
    dataset_path = "outputs/music_final_50_dataset.json"
    results_path = "outputs/evaluation_results.csv"
    summary_path = "outputs/evaluation_summary.json"
    
    with open(dataset_path, "r", encoding="utf-8") as f:
        dataset = json.load(f)
        
    print(f"Loaded {len(dataset)} questions for evaluation.")
    print("WARNING: This may take a while depending on LLM API.")
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    results = []
    total = len(dataset)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        for i, item in enumerate(dataset):
            q = item["question_text"]
            gold = item["gold_answer"]
            print(f"\n[{i+1}/{total}] Q: {q} | Gold: {gold}")
            
            # 1. NoR
            nor_ans = run_nor(q)
            
            # 2. 1-Hop Graph RAG
            try:
                graph1_ans = run_graph_rag_1hop(session, q)
            except Exception as e:
                graph1_ans = f"Error: {e}"
                
            # 3. 2-Hop Graph RAG
            try:
                graph2_ans = run_graph_rag_2hop(session, q)
            except Exception as e:
                graph2_ans = f"Error: {e}"
                
            methods = {
                "NoR": nor_ans,
                "1_Hop_GraphRAG": graph1_ans,
                "2_Hop_GraphRAG": graph2_ans
            }
            
            for method, ans in methods.items():
                em = calculate_exact_match(ans, gold)
                f1 = calculate_f1(ans, gold)
                print(f"  -> {method:15s}: EM={em}, F1={f1:.2f} (Ans: {ans})")
                results.append({
                    "question_id": item.get("question_id", str(i)),
                    "question": q,
                    "gold": gold,
                    "method": method,
                    "prediction": ans,
                    "exact_match": em,
                    "f1_score": f1
                })
                
    driver.close()
    
    # Save results to CSV
    fields = ["question_id", "question", "gold", "method", "prediction", "exact_match", "f1_score"]
    with open(results_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in results:
            writer.writerow(r)
            
    # Calculate aggregation summary
    metrics = {"NoR": {"em":0, "f1":0}, "1_Hop_GraphRAG": {"em":0, "f1":0}, "2_Hop_GraphRAG": {"em":0, "f1":0}}
               
    for m in metrics.keys():
        subset = [r for r in results if r["method"] == m]
        if subset:
            metrics[m]["em"] = sum(r["exact_match"] for r in subset) / len(subset)
            metrics[m]["f1"] = sum(r["f1_score"] for r in subset) / len(subset)
            
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        
    print("\n--- EVALUATION SUMMARY ---")
    for m, vals in metrics.items():
         print(f"{m:15s} -> EM: {vals['em']:.3f} | F1: {vals['f1']:.3f}")
    print(f"\nDetailed CSV saved to {results_path}")

if __name__ == "__main__":
    evaluate()

"""
run_experiments.py - Phase 5 academic alignment

Föydeki 4 yöntemi (NoR, Vanilla RAG, Vanilla QE, KG-Infused RAG) 
ve 4 metriği (Acc, F1, EM, Retrieval Recall) karşılaştırılarak sonuç üretir.
"""
import json
import time
import pandas as pd
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
from metrics import calculate_exact_match, calculate_f1, calculate_accuracy, calculate_retrieval_recall

# Modülleri yükle
from module1_spreading_activation import find_seed, spreading_activation, summarize_subgraph, fetch_entity_descriptions
from module2_query_expansion import expand_query
from module3_answer_generation import generate_answer

def run_nor(question: str):
    """Baseline 1: No-Retrieval"""
    answer = generate_answer(question, context="")
    return {"ans": answer, "retrieved": []}

def run_vanilla_rag(session, question: str):
    """Baseline 2: Vanilla RAG (Using node descriptions as passages)"""
    seed = find_seed(session, question)
    if not seed:
        return {"ans": generate_answer(question, ""), "retrieved": []}
    
    # "Passage" olarak o entity'nin açıklamasını çekiyoruz
    descriptions = fetch_entity_descriptions(session, [seed["entity_id"]])
    context = "\n".join(descriptions)
    answer = generate_answer(question, context)
    return {"ans": answer, "retrieved": descriptions}

def run_vanilla_qe(session, question: str):
    """Baseline 3: Vanilla Query Expansion (LLM expansion but no KG Facts)"""
    expanded_query = expand_query(question, kg_summary="")
    seed = find_seed(session, expanded_query)
    if not seed:
        return {"ans": generate_answer(expanded_query, ""), "retrieved": []}
    
    descriptions = fetch_entity_descriptions(session, [seed["entity_id"]])
    context = "\n".join(descriptions)
    answer = generate_answer(expanded_query, context)
    return {"ans": answer, "retrieved": descriptions}

def run_kg_infused_rag(session, question: str):
    """Main Method: KG-Infused RAG (Full Integration)"""
    seed = find_seed(session, question)
    if not seed:
        return {"ans": generate_answer(question, ""), "retrieved": []}
    
    # 1. Spreading Activation (KG Facts)
    triples = spreading_activation(session, question, seed, max_rounds=2)
    kg_summary = summarize_subgraph(question, triples)
    
    # 2. Query Expansion (KG-Augmented)
    expanded_query = expand_query(question, kg_summary)
    
    # 3. Knowledge Augmentation (KG Facts + Passages)
    involved_node_ids = set([t["source_id"] for t in triples] + [t["target_id"] for t in triples])
    descriptions = fetch_entity_descriptions(session, list(involved_node_ids)[:5]) # Limiting for context length
    
    full_context = f"GRAPH FACTS:\n{kg_summary}\n\nRELEVANT PASSAGES:\n" + "\n".join(descriptions)
    answer = generate_answer(expanded_query, full_context)
    
    return {"ans": answer, "retrieved": triples}

def main():
    with open("outputs/music_final_50_dataset.json", "r", encoding="utf-8") as f:
        questions = json.load(f)

    print(f"Loaded {len(questions)} questions for evaluation.")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    results = []
    methods = ["NoR", "Vanilla_RAG", "Vanilla_QE", "KG_Infused_RAG"]
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            for i, q_item in enumerate(questions):
                q_id = q_item["question_id"]
                query = q_item["question_text"]
                gold = q_item["gold_answer"]
                gold_path = q_item.get("reasoning_path", [])
                
                print(f"\n[{i+1}/{len(questions)}] Q: {query} | Gold: {gold}")
                
                q_res = {"question_id": q_id, "question": query, "gold": gold}
                
                # Run Method 1: NoR
                nor = run_nor(query)
                q_res["NoR"] = {
                    "ans": nor["ans"],
                    "EM": calculate_exact_match(nor["ans"], gold),
                    "F1": calculate_f1(nor["ans"], gold),
                    "Acc": calculate_accuracy(nor["ans"], gold),
                    "Recall": 0.0 # No retrieval done
                }
                
                time.sleep(1) # API Safety
                
                # Run Method 2: Vanilla RAG
                vrag = run_vanilla_rag(session, query)
                q_res["Vanilla_RAG"] = {
                    "ans": vrag["ans"],
                    "EM": calculate_exact_match(vrag["ans"], gold),
                    "F1": calculate_f1(vrag["ans"], gold),
                    "Acc": calculate_accuracy(vrag["ans"], gold),
                    "Recall": calculate_retrieval_recall(vrag["retrieved"], gold_path)
                }
                
                time.sleep(1)
                
                # Run Method 3: Vanilla QE
                vqe = run_vanilla_qe(session, query)
                q_res["Vanilla_QE"] = {
                    "ans": vqe["ans"],
                    "EM": calculate_exact_match(vqe["ans"], gold),
                    "F1": calculate_f1(vqe["ans"], gold),
                    "Acc": calculate_accuracy(vqe["ans"], gold),
                    "Recall": calculate_retrieval_recall(vqe["retrieved"], gold_path)
                }
                
                time.sleep(1)
                
                # Run Method 4: KG-Infused RAG
                kgrag = run_kg_infused_rag(session, query)
                q_res["KG_Infused_RAG"] = {
                    "ans": kgrag["ans"],
                    "EM": calculate_exact_match(kgrag["ans"], gold),
                    "F1": calculate_f1(kgrag["ans"], gold),
                    "Acc": calculate_accuracy(kgrag["ans"], gold),
                    "Recall": calculate_retrieval_recall(kgrag["retrieved"], gold_path)
                }
                
                results.append(q_res)
                
                # Progress Update: Show metrics for this question
                print(f"  -> NoR            : EM={q_res['NoR']['EM']}, F1={q_res['NoR']['F1']:.2f}")
                print(f"  -> Vanilla_RAG    : EM={q_res['Vanilla_RAG']['EM']}, F1={q_res['Vanilla_RAG']['F1']:.2f}, Recall={q_res['Vanilla_RAG']['Recall']:.2f}")
                print(f"  -> Vanilla_QE     : EM={q_res['Vanilla_QE']['EM']}, F1={q_res['Vanilla_QE']['F1']:.2f}, Recall={q_res['Vanilla_QE']['Recall']:.2f}")
                print(f"  -> KG_Infused_RAG : EM={q_res['KG_Infused_RAG']['EM']}, F1={q_res['KG_Infused_RAG']['F1']:.2f}, Recall={q_res['KG_Infused_RAG']['Recall']:.2f}")

                # Intermediate save
                with open("outputs/evaluation_results_full.json", "w", encoding="utf-8") as f_out:
                    json.dump(results, f_out, indent=2, ensure_ascii=False)

    finally:
        driver.close()

    # Calculate Summary Table
    summary = {}
    for m in methods:
        em_list = [r[m]["EM"] for r in results]
        f1_list = [r[m]["F1"] for r in results]
        acc_list = [r[m]["Acc"] for r in results]
        rec_list = [r[m]["Recall"] for r in results]
        
        summary[m] = {
            "EM": sum(em_list)/len(em_list),
            "F1": sum(f1_list)/len(f1_list),
            "Acc": sum(acc_list)/len(acc_list),
            "Recall": sum(rec_list)/len(rec_list)
        }
    
    print("\n" + "="*60)
    print("PHASE 5: FINAL EXPERIMENT RESULTS")
    print("="*60)
    df = pd.DataFrame(summary).T
    df["Avg"] = df.mean(axis=1) # Adding the Avg column as requested in 6.4
    print(df.to_string())
    
    with open("outputs/evaluation_summary_academic.json", "w", encoding="utf-8") as f_sum:
        json.dump(summary, f_sum, indent=2)
        
    print("\nDetailed results saved to: outputs/evaluation_results_full.json")
    print("Summary saved to: outputs/evaluation_summary_academic.json")

if __name__ == "__main__":
    main()

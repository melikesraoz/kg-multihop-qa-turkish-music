import json
import os

DATASET_PATH = "e:/SocialNetworkAnalysis/outputs/music_final_50_dataset.json"

def transform_to_structural(q_item):
    path = q_item["reasoning_path"]
    diff = q_item["difficulty"]
    q_id = q_item["question_id"]
    
    # Path is [S1, R1, T1/S2, R2, T2, ...]
    
    if diff == "2-hop" and len(path) >= 5:
        # Template: [Entity_A]'s [Relation_1]'s [Relation_2] is what?
        e_a = path[0]
        r1 = path[1]
        r2 = path[3]
        return f"{e_a}'s {r1}'s {r2} is what?"
        
    elif diff == "3-hop" and len(path) >= 7:
        # Template: [Entity_A]'s [Relation_1]'s [Relation_2]'s [Relation_3] is what?
        e_a = path[0]
        r1 = path[1]
        r2 = path[3]
        r3 = path[5]
        return f"{e_a}'s {r1}'s {r2}'s {r3} is what?"
        
    elif diff == "comparison":
        # Diversify Comparison Questions (Type 3)
        e_a = path[0]
        # For our specific entities, we'll create varied templates
        if "born" in q_item["question_text"].lower():
            if q_id in ["TR_046", "TR_048", "TR_050"]: # Specific items to make temporal
                return f"Was {e_a} or {path[-3]} born earlier?"
            else:
                return f"Which artist was born in {path[-1]}, {e_a} or {path[-3]}?"
        return q_item["question_text"]
        
    return q_item["question_text"]

def main():
    if not os.path.exists(DATASET_PATH):
        print("Dataset not found.")
        return

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        original = item["question_text"]
        new_q = transform_to_structural(item)
        item["question_text"] = new_q
        print(f"Transformed: {original} -> {new_q}")

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Dataset transformation complete!")

if __name__ == "__main__":
    main()

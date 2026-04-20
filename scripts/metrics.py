"""
metrics.py
Standard QA Evaluation Metrics (SQuAD style)
"""
import re
import string

def normalize_answer(s):
    """
    Lower text and remove punctuation, articles and extra whitespace.
    """
    def lower(text):
        return text.lower()

    def remove_punc(text):
        exclude = set(string.punctuation)
        return "".join(ch for ch in text if ch not in exclude)

    def white_space_fix(text):
        return " ".join(text.split())

    def remove_articles(text):
        return re.sub(r"\b(a|an|the)\b", " ", text)

    def turkish_chars_fix(text):
        return text.replace('ı', 'i').replace('ü', 'u').replace('ö', 'o').replace('ş', 's').replace('ç', 'c').replace('ğ', 'g')

    def semantic_fix(text):
        # Turkey/Türkiye variations are the most common source of false negatives
        return re.sub(r'\b(turkey|turkiye|turkiye)\b', 'turkiye', text)

    if not isinstance(s, str):
        return str(s)
        
    normalized = white_space_fix(remove_articles(remove_punc(lower(s))))
    return semantic_fix(turkish_chars_fix(normalized))

def calculate_exact_match(prediction, truth):
    return int(normalize_answer(prediction) == normalize_answer(truth))

def calculate_f1(prediction, truth):
    pred_tokens = normalize_answer(prediction).split()
    truth_tokens = normalize_answer(truth).split()
    
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)
        
    import collections
    common = collections.Counter(pred_tokens) & collections.Counter(truth_tokens)
    num_same = sum(common.values())
    
    if num_same == 0:
        return 0.0
        
    precision = 1.0 * num_same / len(pred_tokens)
    recall = 1.0 * num_same / len(truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1

def calculate_retrieval_recall(retrieved_items, gold_reasoning_path):
    """
    Calculates how many of the relevant facts were successfully retrieved.
    gold_reasoning_path: list of strings [S1, R1, T1/S2, R2, T2, ...]
    retrieved_items: list of triple dicts (KG) or list of strings (Vanilla RAG)
    """
    if not gold_reasoning_path:
        return 1.0
        
    # Convert gold string sequence into a set of triple keys "Source-Relation-Target"
    gold_triples = []
    # If it's [A, R1, B, R2, C], we have (A,R1,B) and (B,R2,C)
    for i in range(0, len(gold_reasoning_path) - 2, 2):
        s = str(gold_reasoning_path[i]).lower()
        r = str(gold_reasoning_path[i+1]).lower()
        t = str(gold_reasoning_path[i+2]).lower()
        gold_triples.append(f"{s}-{r}-{t}")
    
    if not gold_triples:
        return 1.0

    if isinstance(retrieved_items, list) and len(retrieved_items) > 0 and isinstance(retrieved_items[0], dict):
        # KG Style: retrieved_items is a list of dicts with source_name, relation_name, target_name
        def to_key(x):
            s = str(x.get('source_name', '')).lower()
            r = str(x.get('relation_name', '')).lower()
            t = str(x.get('target_name', '')).lower()
            return f"{s}-{r}-{t}"
            
        retrieved_keys = [to_key(it) for it in retrieved_items]
        found = sum(1 for gk in gold_triples if gk in retrieved_keys)
        return found / len(gold_triples)
    else:
        # Vanilla Style: Check if the entities/relations from the gold path are in the retrieved text
        retrieved_text = " ".join(retrieved_items).lower() if isinstance(retrieved_items, list) else str(retrieved_items).lower()
        # For simplicity, if the key parts of the reasoning path appear in the text
        important_nodes = [str(x).lower() for i, x in enumerate(gold_reasoning_path) if i % 2 == 0]
        found = sum(1 for node in important_nodes if node in retrieved_text)
        return found / len(important_nodes)

def calculate_accuracy(prediction, truth):
    return calculate_exact_match(prediction, truth)

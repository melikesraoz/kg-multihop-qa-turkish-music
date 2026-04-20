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
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    if not isinstance(s, str):
        return str(s)
        
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def calculate_exact_match(prediction, truth):
    return int(normalize_answer(prediction) == normalize_answer(truth))

def calculate_f1(prediction, truth):
    pred_tokens = normalize_answer(prediction).split()
    truth_tokens = normalize_answer(truth).split()
    
    # if either the prediction or the truth is no-answer then f1 = 1 if they agree, 0 otherwise
    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)
        
    common_tokens = set(pred_tokens) & set(truth_tokens)
    num_same = sum(1 for t in pred_tokens if t in common_tokens) # To handle duplicates correctly, but set intersection is simpler.
    
    # Actually, proper SQuAD F1 uses Counter
    import collections
    common = collections.Counter(pred_tokens) & collections.Counter(truth_tokens)
    num_same = sum(common.values())
    
    if num_same == 0:
        return 0.0
        
    precision = 1.0 * num_same / len(pred_tokens)
    recall = 1.0 * num_same / len(truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1

def calculate_accuracy(prediction, truth, model="llm"):
    """
    Accuracy generally uses exact match or strict heuristics.
    In QA, EM is the accuracy. For generative QA, sometimes LLM-as-a-judge is used.
    Here we rely just on Exact Match.
    """
    return calculate_exact_match(prediction, truth)

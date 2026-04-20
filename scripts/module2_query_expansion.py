"""
module2_query_expansion.py - Pure Graph Query Expansion

Graf uzerinden cikarilan alt grafi (subgraph) ve orijinal soruyu alarak,
sistemin odaklanmasi gereken yeni ve daha belirgin bir soru jenerasyonu
(Graph-augmented query expansion) yapar.
"""
from llm_client import ask_llm

def expand_query(original_query: str, kg_summary: str = "") -> str:
    """Graf ozetiyle (varsa) soruyu daha belirgin hale getirerek 'Query Expansion' yapar."""
    if not kg_summary or "No relevant graph facts found" in kg_summary:
        prompt = f"""You are an AI assistant. Rewrite the following question to make it more descriptive and clear for a retrieval system. 
Stay true to the original intent but add potential synonyms or clarifications if needed.
Original Question: "{original_query}"
Reply with ONLY the rewritten question.
"""
    else:
        prompt = f"""You are an expert NLP system for a Knowledge Graph.
Original Question: "{original_query}"
Knowledge Graph Context:
{kg_summary}

Rewrite the original question so it incorporates the exact entities and relationships mentioned in the Graph Context, making it highly specific for the final answer generator.
Reply with ONLY the rewritten question. Do not answer it yet.
"""
    try:
        expanded = ask_llm(prompt)
        return expanded
    except Exception:
        return original_query

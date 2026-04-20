"""
module3_answer_generation.py - Pure Graph Answer Generation

Graf uzerinden toplanan bilgileri kullanarak 
son cevabi uretir. Hicbir sekilde harici metin (corpus) kullanmaz.
"""
from llm_client import ask_llm

def generate_answer(query: str, kg_summary: str) -> str:
    """Nihai cevabi yalnizca Neo4j graf ozetine bakarak uretir."""
    prompt = f"""You are a GraphRAG Expert. Based STRICTLY on the Knowledge Graph Facts provided below, answer the user's question as accurately and concisely as possible.
If the graph facts do not contain the answer, say "The provided graph data does not contain the answer."

Knowledge Graph Facts:
{kg_summary}

Question: "{query}"

Instruction: Provide ONLY the answer. Do not add conversational filler.
Answer:"""
    try:
        return ask_llm(prompt)
    except Exception as e:
        return f"[Error generating answer: {e}]"

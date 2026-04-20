from llm_client import ask_llm

def generate_answer(query: str, context: str) -> str:
    """Nihai cevabi verilen bağlama (graf özeti veya metin pasajı) bakarak üretir."""
    if not context or context.strip() == "":
        prompt = f"""You are an expert AI. Please answer the following question based on your internal knowledge.
Question: "{query}"
Instruction: Provide ONLY the answer. Do not add conversational filler.
Answer:"""
    else:
        prompt = f"""You are an expert AI. Based on the CONTEXT provided below (which may include Knowledge Graph facts or Wikipedia passages), answer the user's question as accurately and concisely as possible.

CONTEXT:
{context}

Question: "{query}"

Instruction: Provide ONLY the answer. Do not add conversational filler. If the context does not contain the answer, use your knowledge but prioritize the context if it is relevant.
Answer:"""
    
    try:
        return ask_llm(prompt)
    except Exception as e:
        return f"[Error generating answer: {e}]"

"""LLM prompt construction for RAG."""

SYSTEM_PROMPT = """You are a helpful website assistant.
Answer questions ONLY using the provided context from the website and documents.
If the answer is not in the context, say you don't know and suggest where the user might look.
Always include a short Sources list at the end with URLs or file paths."""


def build_prompt(question: str, context_blocks: list[str]) -> str:
    """
    Build the user prompt with question and context.

    Args:
        question: User's question
        context_blocks: List of context blocks (each with source, title, content)

    Returns:
        Formatted prompt string
    """
    context_text = "\n---\n".join(context_blocks)
    return f"Question: {question}\n\nContext:\n{context_text}"

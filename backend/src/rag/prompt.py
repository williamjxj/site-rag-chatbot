"""LLM prompt construction for RAG."""

from ..config import settings

# Use system prompt from settings (configurable via SYSTEM_PROMPT environment variable)
SYSTEM_PROMPT = settings.system_prompt


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

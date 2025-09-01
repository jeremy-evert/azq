# azq/token_counter.py
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Return approximate token count for a given string and model."""
    enc = tiktoken.encoding_for_model(model)
    return len(enc.encode(text))


from tiktoken import get_encoding as tiktoken_get_encoding


def count_tokens(text):
    tokenizer = tiktoken_get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    token_count = len(tokens)
    return token_count

from nltk.tokenize import word_tokenize
from langchain_core.chat_history import InMemoryChatMessageHistory

def count_history(chat_history: InMemoryChatMessageHistory) -> int:
    total_tokens = 0
    for message in chat_history.messages:
        # Tokenize the content of each message and count the tokens
        tokens = word_tokenize(message.content)
        total_tokens += len(tokens)
    return total_tokens

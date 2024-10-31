from transformers import pipeline


def load_qa_model():
    return pipeline("question-answering", model="bert-large-uncased-whole-word-masking-finetuned-squad")


def load_summary_model():
    return pipeline("summarization", model="google/mt5-small", tokenizer="t5-small")

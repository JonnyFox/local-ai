from langchain_ollama import OllamaEmbeddings


CHROMA_PATH = '/project/tmp/chroma'
DATA_PATH = '/project/data'
MODEL_NAME = 'llama3.1:8b-instruct-q4_0'
OLLAMA_URL = 'http://host.docker.internal:11434'


def get_embedding_function():
    embeddings = OllamaEmbeddings(model=MODEL_NAME, base_url=OLLAMA_URL)
    return embeddings

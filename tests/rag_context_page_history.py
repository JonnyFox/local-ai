import requests
from elasticsearch import Elasticsearch
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.llms.ollama import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from samples.settings import CHROMA_PATH, MODEL_NAME, MODEL_URL, get_embedding_function

SYSTEM_PROMPT = """
    You are the best assistant of the XYZ Web Portal for question-answering tasks.
    Respond ALWAYS to the user's questions with the language they used for the question. 
    Respond in a clear, precise, and polite manner.
    Answer only questions related to the XYZ Web Portal.
    If you do not have enough information to answer the question, apologize for not having found the answer and advise the user to contact support.
    """


# Answer the following question (enclosed in the "question" tag) using the information in the "context" tag.
HISTORY_TEMPLATE = """
<Question>
{question}
</Question>

<AI>
{ai}
</AI>
"""

PROMPT_TEMPLATE = """
Use the following Context to answer the question using the same language as the Question. Consider the History as well.

<History>
{history}
</History>

<Context>
{context}
</Context>

<Question>
{question}
</Question>
"""
context = ''
history = ''
db = None


def prepare_database():
    global db
    if not db:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def answer_question(query_text, context):
    global history
    # results = db.similarity_search_with_score(query_text, k=5)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(query_text)

    llm = Ollama(model=MODEL_NAME, system=SYSTEM_PROMPT, base_url=MODEL_URL)
    # context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    # prompt = ChatPromptTemplate.from_messages(
    #     [
    #         ("system", SYSTEM_PROMPT),
    #         MessagesPlaceholder("chat_history"),
    #         MessagesPlaceholder("context", context_text),
    #         ("user", "{input}"),
    #     ]
    # )

    prompt_chain = {"context": retriever | format_docs, "history": RunnablePassthrough(), "question": RunnablePassthrough()} | prompt

    rag_chain = prompt_chain | llm | StrOutputParser()
    # prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt)

    response_text = ""

    for chunk in rag_chain.stream({"question": query_text, "history": history}):
        response_text += chunk
        print(chunk, end="", flush=True)

    history += ChatPromptTemplate.from_template(HISTORY_TEMPLATE).format(question=query_text, ai=response_text)

    if len(retrieved_docs) > 0:
        sources = [doc.metadata.get("id", None) for doc in retrieved_docs]
        print(f"\nSources: {sources}")


def main():
    global context
    prepare_database()
    while True:
        question = input('Ask: ')
        if question.lower() == '/exit':
            break
        answer = answer_question(question, context)


if __name__ == "__main__":
    main()

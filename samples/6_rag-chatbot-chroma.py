import os
from langchain_ollama import ChatOllama, OllamaEmbeddings

from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from settings import CHROMA_PATH, DATA_PATH, OLLAMA_URL, get_embedding_function

SYSTEM_PROMPT = """
    You are the best assistant of the XYZ Web Portal for question-answering tasks.
    Respond ALWAYS to the user's questions with the language they used for the question. 
    Respond in a clear, precise, and polite manner.
    Answer only questions related to the XYZ Web Portal.
    If you do not have enough information to answer the question, apologize for not having found the answer and advise the user to contact support.
    """

SYSTEM_TEMPLATE = """
    You are the best assistant of the XYZ Web Portal for question-answering tasks.
    Answer ALWAYS to the user's questions with the language they used in the question. 
    Answer in a clear, precise, and polite manner.
    Answer only questions related to the XYZ Web Portal.
    Answer user questions using the following context. 
    If the context do not have enough information to answer the question, apologize for not having found the answer and advise the user to contact support.

    <context>
    {context}
    </context>
  """

context = ''
chat_history = ChatMessageHistory()
db = None


def prepare_database():
    global db
    if not db:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def answer_question(query_text, context):
    global chat_history

    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(query_text)

    llm = ChatOllama(model="llama3.1", base_url=OLLAMA_URL)
    prompt = ChatPromptTemplate.from_messages(
        [
            ('system', SYSTEM_TEMPLATE),
            MessagesPlaceholder("messages"),
        ]
    )

    document_chain = create_stuff_documents_chain(llm, prompt)

    chat_history.add_user_message(query_text)

    response_text = ""

    print("\n✨: ", end="")

    for chunk in document_chain.stream({"messages": chat_history.messages, 'context': retrieved_docs}):
        response_text += chunk
        print(chunk, end="", flush=True)

    chat_history.add_ai_message(response_text)

    print("\n")

    # print("\n\nRetrieved Documents reference:\n")

    # if len(retrieved_docs) > 0:
    #     sources = [doc.metadata.get("id", None) for doc in retrieved_docs]
    #     for source in sources:
    #         print(f" - 🔖 {source}")
    #     print("\n")


def chatbot():
    print('\033[H\033[J')

    global context
    prepare_database()

    print('Welcome to the Simple Chatbot! Type `exit` to end the conversation.\n')

    while True:
        query = input('👨: ')

        if query.lower() == 'exit':
            print('Ending conversation. Goodbye!')
            break

        answer_question(query, context)


# Run the chatbot
if __name__ == "__main__":
    chatbot()

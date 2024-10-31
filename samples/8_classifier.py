import os, json
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.llms.ollama import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.chains.combine_documents import create_stuff_documents_chain

json_schema = {
    'type': 'object',
    'properties': {
        'category': {'type': 'string', 'description': 'The category of the question (manual, order, product)'},
        'order_id': {'type': 'string', 'description': 'The ID of the order if the category is order otherwise it is null'},
        'product_id': {'type': 'string', 'description': 'The ID of the product if the category is product otherwise it is null'},
        'product_name': {'type': 'string', 'description': 'The name of the product if the category is product otherwise it is null'},
        'manual_question': {'type': 'string', 'description': 'The original human question if the category is manual otherwise it is null'},
        'confidence': {'type': 'number', 'description': 'A float value between 0 and 1 that represents the confidence of the classification'},
    },
    'required': ['category', 'confidence'],
}


CHROMA_PATH = '/project/chroma'
DATA_PATH = '/project/data'
OLLAMA_URL = 'http://host.docker.internal:11434'

SYSTEM_TEMPLATE = '''
    You act as a classification algorithm for the Question coming from user.
    You have to classify the question in one of the following categories:
    - manual
    - order
    - product

    Answer to the Question considering also the History of the conversation.
    Your answer MUST BE a JSON object with the following structure:

    <json_schema>
    {{schema}}
    </json_schema>
   
    No other formats or notes than the one described above are allowed in your answer.
    If you do not have enough information to answer the question, the confidence value must be 0 and the category must be 'manual'.
  '''

PROMPT_TEMPLATE = '''
  Answer to the Question considering also the following History.
  Answer to the Question considering also the following History USING ONLY the json_schema defined in the System Prompt.
  If the question asks about the last order or product, provide the information using the last order or product in the History.

  <history>
  {history}
  </history>

  <question>
  {question}
  </question>
  '''

context = ''
chat_history = ChatMessageHistory()
db = None


def answer_question(query_text, context):
    global chat_history

    # retriever = db.as_retriever(search_type='similarity', search_kwargs={'k': 5})
    # retrieved_docs = retriever.invoke(query_text)

    system_prompt = SYSTEM_TEMPLATE.format(schema=json.dumps(json_schema, indent=2))

    classifier = Ollama(
        model='llama3.1',
        format='json',
        system=system_prompt,
        base_url=OLLAMA_URL,
        temperature=0,
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    # rag_chain = {'context': retriever | format_docs, 'history': RunnablePassthrough(), 'question': RunnablePassthrough()} | prompt | llm | StrOutputParser()
    # prompt = prompt_template.format(context=context_text, question=query_text)
    # print(prompt.invoke({'history': chat_history.messages, 'question': query_text}))

    classification_chain = prompt | classifier | JsonOutputParser()

    response_text = ''

    response = classification_chain.invoke({'history': chat_history.messages, 'question': query_text})
    response_text = str(response)
    print(f'\n✨: {response_text}\n')

    chat_history.add_user_message(query_text)
    chat_history.add_ai_message(response_text)

    # if len(retrieved_docs) > 0:
    #     sources = [doc.metadata.get('id', None) for doc in retrieved_docs]
    #     print(f'\nSources: {sources}')


def main():
    global context

    os.system('CLS') if os.name == 'nt' else os.system('clear')
    while True:
        question = input('Human: ')
        if question.lower() == '/exit':
            break
        answer = answer_question(question, context)


if __name__ == '__main__':
    main()

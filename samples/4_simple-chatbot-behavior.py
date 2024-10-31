# Import necessary libraries
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langdetect import detect
from typing_extensions import Annotated, TypedDict
from typing import Sequence
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

OLLAMA_URL = 'http://host.docker.internal:11434'

model = ChatOllama(model='llama3.1:latest', base_url=OLLAMA_URL)

prompt = ChatPromptTemplate.from_messages(
    [
        ('system', 'You talk like a medieval king. Answer all questions to the best of your ability.'),
        # ('system', 'You talk like a roman emperor. Answer all questions to the best of your ability. ALWAYS answer in language code `{language}`.'),
        MessagesPlaceholder(variable_name='messages'),
    ]
)


class CustomMessageState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str


def call_model(state):
    chain = prompt | model
    response = chain.invoke(state)
    return {'messages': response}


def setup_workflow():
    workflow = StateGraph(state_schema=CustomMessageState)
    workflow.add_edge(START, 'model')
    workflow.add_node('model', call_model)
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def chatbot():
    print('\033[H\033[J')

    workflow = setup_workflow()
    config = {'configurable': {'thread_id': 'abc123'}}

    print('Welcome to the Simple Chatbot! Type `exit` to end the conversation.\n')

    while True:
        query = input('👨: ')

        # language = detect(query)

        if query.lower() == 'exit':
            print('Ending conversation. Goodbye!')
            break

        input_messages = [HumanMessage(query)]

        print(f"\n✨: ", end="")

        # for chunk, metadata in workflow.stream({'messages': input_messages, 'language': language}, config, stream_mode='messages'):
        for chunk, metadata in workflow.stream({'messages': input_messages}, config, stream_mode='messages'):
            if isinstance(chunk, AIMessage):
                print(chunk.content, end='', flush=True)

        print('\n')


# Run the chatbot
if __name__ == '__main__':
    chatbot()

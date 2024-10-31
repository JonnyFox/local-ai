from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent

from settings import CHROMA_PATH, DATA_PATH, OLLAMA_URL, get_embedding_function

llm = ChatOllama(model="llama3.1", base_url=OLLAMA_URL)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            'system',
            'You are a helpful assistant that can perform simple math operations like addition, multiplication, and exponentiation. You can also answer questions about math.',
        ),
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        MessagesPlaceholder(variable_name='input'),
        MessagesPlaceholder(variable_name='agent_scratchpad', optional=True),
    ]
)


@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers together."""
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b


@tool
def exp(base: int, exponent: int) -> int:
    """Raise a base to an exponent."""
    return base**exponent


tools = [multiply, add, exp]


agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
# These functions do the same as the following commented code
#
#  agent = (
#         RunnablePassthrough.assign(
#             agent_scratchpad=lambda x: message_formatter(x["intermediate_steps"])
#         )
#         | prompt
#         | llm_with_tools
#         | ToolsAgentOutputParser()
#     )


def answer_question(query_text):
    response = agent_executor.invoke(
        {
            'input': [HumanMessage(content=query_text)],
        }
    )
    return response['output']


def chatbot():
    print('\033[H\033[J')

    print('Welcome to the Simple Chatbot! Type `exit` to end the conversation.\n')

    while True:
        query = input('👨: ')

        if query.lower() == 'exit':
            print('Ending conversation. Goodbye!')
            break

        response = answer_question(query)
        print(f"\n✨: {response}\n")


# Run the chatbot
if __name__ == "__main__":
    chatbot()

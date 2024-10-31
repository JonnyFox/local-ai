# Import necessary libraries
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.checkpoint.memory import MemorySaver

OLLAMA_URL = 'http://host.docker.internal:11434'

model = ChatOllama(model="llama3.1:latest", base_url=OLLAMA_URL)

workflow = StateGraph(state_schema=MessagesState)


def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}


def setup_workflow():

    # Define a new graph
    workflow.add_edge(START, "model")

    # This is the node that will call the model
    workflow.add_node("model", call_model)

    # Other nodes can be added here to perform additional processing

    # Add memory
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


def chatbot():
    print("\033[H\033[J")

    # Add graph memory
    graph = setup_workflow()
    config = {"configurable": {"thread_id": "abc123"}}

    print("Welcome to the Simple Chatbot! Type 'exit' to end the conversation.\n")

    while True:
        query = input("👨: ")

        if query.lower() == "exit":
            print("Ending conversation. Goodbye!")
            break

        input_messages = [HumanMessage(query)]

        print(f"\n✨: ", end="")

        for chunk, metadata in graph.stream({"messages": input_messages}, config, stream_mode='messages'):
            if isinstance(chunk, AIMessage):
                print(chunk.content, end="", flush=True)

        print("\n")


# Run the chatbot
if __name__ == "__main__":
    chatbot()

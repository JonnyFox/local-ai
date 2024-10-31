# Import necessary libraries
from langchain.prompts import PromptTemplate
from langchain_ollama import ChatOllama

OLLAMA_URL = 'http://host.docker.internal:11434'

# Create a prompt template for the chatbot
prompt_template = PromptTemplate(input_variables=["query"], template="You are a helpful chatbot. Respond to the user's question: {query}")

model = ChatOllama(model="llama3.1:latest", base_url=OLLAMA_URL)


def call_model(query):
    for token in model.stream(query):
        print(token.content, end="", flush=True)


def chatbot():
    # clear console
    print("\033[H\033[J")

    print("Welcome to the Simple Chatbot! Type 'exit' to end the conversation.\n")

    while True:
        # Get user input
        query = input("👨: ")

        if query.lower() == "exit":
            print("Ending conversation. Goodbye!")
            break

        print(f"\n✨: ", end="")
        call_model(query)

        print("\n")


# Run the chatbot
if __name__ == "__main__":
    chatbot()

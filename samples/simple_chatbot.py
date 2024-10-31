import asyncio

from langchain.schema import ChatMessage
from langchain_ollama import ChatOllama
from langchain_community.chat_message_histories import ChatMessageHistory

class OllamaChatCompletionService:
    async def get_chat_message_content(self, history: ChatMessageHistory) -> ChatMessage:
        return self.model.invoke(history)

model = ChatOllama(model="llama3.1:latest", base_url="http://localhost:11434")

chat_service = OllamaChatCompletionService(model)

history = ChatMessageHistory()
history.add_message("system", "You are a helpful assistant that will help you with your questions.")

async def main():
    while True:
        user_message = input("👨: ")

        if not user_message.strip():
            break

        history.add_message("user", user_message)

        response = await chat_service.get_chat_message_content(history)

        print(f"✨: {response.content}")

        history.add_message(response.role, response.content)

asyncio.run(main())





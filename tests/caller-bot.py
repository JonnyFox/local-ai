# create a bot that calls the chatbot API to answer questions
# Here a list of common questions in italian
# questions = [
#     "Chi sei?",
#     "Cosa è il Portale Web XYZ?",
#     "Come posso registrarmi?",
#     "Come posso contattare il supporto?",
#     "Come posso fare un ordine?",
#     "Come posso inserire una fattura?",
#  ]
# This script will simulate 10 concurrent users asking questions to the bot

import time
import requests
import multiprocessing
import random

CONCURRENT_USERS = 1
RANDOM = False

lock = multiprocessing.Lock()


def caller_bot(response_time, lock):
    # create a bot that calls the chatbot API to answer questions
    # Here a list of common questions in italian
    questions = [
        "Chi sei?",
        "Cosa è il Portale Web XYZ?",
        "Come posso registrarmi?",
        "Come posso contattare il supporto?",
        "Come posso mandare un messaggio?",
        "Come posso inserire una fattura?",
        "Come posso cancellare un utente?",
        "Cosa posso fare come amministratore?",
        "Cosa non può fare un amministratore?",
    ]

    questions_en = [
        "Who are you?",
        "What is the XYZ Web Portal?",
        "How can I register?",
        "How can I contact support?",
        "How can I send a message?",
        "How can I insert an invoice?",
        "How can I delete a user?",
        "What can I do as an administrator?",
        "What can't an administrator do?",
    ]

    # This script will simulate 10 parallel users asking questions to the bot
    with multiprocessing.Pool(processes=CONCURRENT_USERS) as pool:
        # simulate 10 parallel users asking questions to the bot
        pool.starmap(ask_question, [(questions, i, response_time) for i in range(CONCURRENT_USERS)])


def ask_question(questions, chat_id, response_time):
    ## pick a random question from the list and ask the chatbot
    for i in range(len(questions)):
        question = random.sample(questions, 1)[0] if RANDOM else questions[i]
        # time.sleep(random.randint(1, 5))
        print(f"Chat {chat_id} - User: {question}")
        start = time.time()
        answer = call_chatbot_api(question, chat_id)
        elapsed_time = time.time() - start

        with lock:
            response_time['answered_questions'] += 1
            response_time['sum'] += elapsed_time

        print(f"Chat {chat_id} - ✨: {answer}")
        print(f"Chat {chat_id} - Elapsed time: {elapsed_time}")
        time.sleep(1)


def call_chatbot_api(question, chat_id):
    # call the chatbot API to get the answer
    resp = requests.post("http://localhost:8000/api/search/", data={'query': question, 'chat_uuid': chat_id})

    # consider that the response is a stream of text chunks
    # so we need to concatenate all the chunks to get the full answer
    return resp.content.decode()


def main():
    manager = multiprocessing.Manager()

    response_time = manager.dict()
    response_time["sum"] = 0
    response_time["answered_questions"] = 0

    caller_bot(response_time, lock)
    print("----------------------------------------")
    print(f'Concurrent users: {CONCURRENT_USERS}')
    print(f'Total number of questions answered: {response_time["answered_questions"]}')
    print(f'Average response time: {response_time["sum"] / response_time["answered_questions"]}')


if __name__ == "__main__":
    main()

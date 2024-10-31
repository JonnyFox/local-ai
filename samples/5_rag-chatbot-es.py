import requests
from elasticsearch import Elasticsearch
from langdetect import detect

OLLAMA_API_URL = 'http://host.docker.internal:11434'

es = Elasticsearch(
    'https://es01:9200',
    ca_certs='/project/http_ca.crt',
    basic_auth=('elastic', 'gy7GcoMzE9YGeAecXS7T'),
)


def answer_question(question, context):
    detected_language = detect(question)

    # Ricerca su Elasticsearch
    res = es.search(
        index='manuals2',
        body={
            'query': {
                'bool': {
                    'must': [
                        {'match': {'content': question}},
                        {'match': {'language': detected_language}},
                        {'match': {'is_header': False}},
                    ]
                }
            }
        },
    )

    # Aggiunta dei risultati della ricerca al contesto
    search = ' '.join([hit['_source']['content'] for hit in res['hits']['hits']])

    # Creazione del prompt
    prompt = f'{context}\nRicerca: {search}\nDomanda: {question}\nRisposta:'

    # Richiesta all'API di Ollama
    response = requests.post(
        f'{OLLAMA_API_URL}/api/generate',
        json={
            'model': 'llama3.1:latest',
            'prompt': prompt,
            'stream': False,
            'system': '''
              Sei l'assistente virtuale del portale web di Creazione Fatture.
              Rispondi alle domande degli utenti in modo chiaro, preciso e gentile, utilizzando le informazioni che trovi nel prompt dopo il testo "Ricerca:" e prima del testo "Domanda:" per ogni domanda che ti viene rivolta.
              Le informazioni che trovi nel prompt dopo il testo "Ricerca:" e prima del testo "Domanda:" possono utilizzare il 'voi', in questo caso convertile utilizzando il 'tu'.
              Rispondi solo a domande riguardanti il portale Web di Creazione Fatture e se non hai informazioni sufficienti per rispondere alla domanda, rispondi con "Mi dispiace, non ho informazioni su questo argomento" o una cosa simile.
              ''',
        },
    )

    if response.status_code == 200:
        answer = response.json().get('response', '').strip()
        return answer, f'{context}\n\nDomanda: {question}\nRisposta: {answer}'
    else:
        return 'Errore nella generazione della risposta', context


def chatbot():
    print('\033[H\033[J')

    print('Welcome to the Simple Chatbot! Type `exit` to end the conversation.\n')

    context = ''

    while True:
        query = input('👨: ')

        if query.lower() == 'exit':
            print('Ending conversation. Goodbye!')
            break

        answer, context = answer_question(query, context)
        print(f'\n✨: {answer}\n')


# Run the chatbot
if __name__ == '__main__':
    chatbot()

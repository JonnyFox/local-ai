## Overview
This project includes various scripts and configurations for setting up and running a chatbot application using Docker, Elasticsearch, and other tools.

## Directory Structure
- `docker-compose.yml`: Docker Compose configuration file.
- `data/`: Directory for storing data files.
- `samples/`: Contains sample Python scripts for various chatbot functionalities.
  - `1_simple-chatbot.py`: Basic chatbot example.
  - `2_simple-chatbot-stream.py`: Chatbot with streaming responses.
  - `3_simple-chatbot-stream-memory.py`: Chatbot with memory and streaming responses.
  - `4_simple-chatbot-behavior.py`: Chatbot with behavior customization.
  - `5_rag-chatbot-es-pop-es.py`: Chatbot with Elasticsearch integration.
  - `6_rag-chatbot-chroma-pop-db.py`: Chatbot with Chroma database integration.
- `tests/`: Directory for test files.
- `tmp/`: Temporary files.
- `web_server/`: Contains server-related files and configurations.

## Setup
1. Start the Docker containers:
   ```sh
   docker-compose up -d
    ```
2. Connect your IDE to the `dev` Docker container (for VSCode install the `Remote - Containers` extension and select `Reopen in Container`).
3. Open one sample Python script in the `samples/` directory (for VSCode just select the script in the `Run and Debug` tab and hit `F5`).

## Web server usage

1. Start the front-end server:
   ```sh
   cd web_server/web
   nr start
   ```
2. Start the back-end server selecting `Server - Django` in the `Run and Debug` tab, then hit `F5`.
3. Open the web UI in your browser at [http://localhost:8080](http://localhost:8080)
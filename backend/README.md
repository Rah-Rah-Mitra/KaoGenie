# SmartExam - Backend Service

This directory contains the FastAPI backend for the SmartExam project. It handles all data ingestion, agent-based exam generation, and communication with the frontend via a streaming API.

> **Note:** For full project setup, including system dependencies like Tesseract and Node.js for the frontend, please refer to the [main README.md](../README.md) at the root of the project.

## Running the Backend Server

To run the backend service in isolation, follow these steps from the `backend` directory:

1.  **Ensure prerequisites from the main README are installed.** This includes Python 3.11 and `uv`.

2.  **Set up the Python environment:**
    ```sh
    # Create the virtual environment
    uv venv

    # Activate the environment
    # On macOS/Linux/WSL:
    source .venv/bin/activate
    # On Windows (CMD/PowerShell):
    # .venv\Scripts\activate

    # Install dependencies
    uv pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Make sure you have a `.env` file in this directory with valid API keys. You can copy it from the example:
    ```sh
    cp .env.example .env
    ```

4.  **Start the server:**
    The server will run on `http://127.0.0.1:8000`.
    ```sh
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ```
    You can access the interactive API documentation at `http://127.0.0.1:8000/docs`.

## Key Modules

-   `/src/deep_searcher/agents`: Contains the core logic for each specialized AI agent.
-   `/src/deep_searcher/data_pipeline`: Manages web searching, crawling, and processing of source documents.
-   `/src/deep_searcher/vector_store`: Handles interactions with the ChromaDB vector store.
-   `/prompts`: Stores the system prompts that define the behavior of each agent.
-   `main.py`: The FastAPI application entry point, defining API endpoints and orchestrating the generation process.
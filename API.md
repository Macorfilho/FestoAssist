
# API Documentation - FestoTech Assistant

This document provides detailed information about the API endpoints for the FestoTech Assistant. It is intended for frontend developers who need to integrate with this backend.

## Base URL

The API is served from the root of the application. When running locally, the base URL is `http://localhost:8000`.

---

## Endpoints

### 1. Chat

This is the main endpoint for interacting with the assistant.

- **URL:** `/chat`
- **Method:** `POST`
- **Description:** Sends a question to the assistant and receives a response based on the provided documents. It maintains a conversation history using a `session_id`.

#### Request Body

The request body must be a JSON object with the following fields:

| Field        | Type   | Description                                                                 | Required |
|--------------|--------|-----------------------------------------------------------------------------|----------|
| `question`   | String | The question you want to ask the assistant.                                 | Yes      |
| `session_id` | String | A unique identifier for the conversation session. This is used to maintain context. | Yes      |

**Example:**

```json
{
  "question": "What is the piston diameter of the DSNU actuator?",
  "session_id": "user123_session456"
}
```

#### Responses

- **Success (200 OK):**

  The response will be a JSON object containing the assistant's answer.

  ```json
  {
    "answer": "The piston diameter of the DSNU actuator can vary. According to the documentation, there are models with diameters of 8, 10, 12, 16, 20, and 25 mm."
  }
  ```

- **Error (400 Bad Request):**

  This error occurs if the request body is not a valid JSON or if required fields are missing.

  ```json
  {
    "error": "Required fields are missing: question, session_id"
  }
  ```

- **Error (500 Internal Server Error):**

  This error occurs if the assistant is not initialized correctly or if there is an issue processing the request.

  ```json
  {
    "error": "The agent was not initialized correctly. Check the server logs."
  }
  ```

---

### 2. Health Check

This endpoint is used to verify the status of the API.

- **URL:** `/health`
- **Method:** `GET`
- **Description:** Returns the operational status of the assistant.

#### Responses

- **Success (200 OK):**

  Indicates that the assistant is running and ready to receive requests.

  ```json
  {
    "status": "ok",
    "message": "FestoTech Assistant is operational."
  }
  ```

- **Error (500 Internal Server Error):**

  Indicates that the assistant is not operational. This could be due to a configuration error or a problem during initialization.

  ```json
  {
    "status": "error",
    "message": "FestoTech Assistant is not operational."
  }
  ```

## How to Run the Project Locally

To run the project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd FestoAssist
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Start Redis with Docker:**
    ```bash
    docker run -d -p 6379:6379 --name redis-festo redis
    ```

4.  **Configure environment variables:**
    -   Copy the `.env.example` file to `.env`.
    -   Add your `GOOGLE_API_KEY` to the `.env` file.

5.  **Build the vector database:**
    ```bash
    python build_vectorstore.py
    ```

6.  **Start the Flask server:**
    ```bash
    python app.py
    ```

The server will be available at `http://localhost:8000`.

## Error Handling

- **400 Bad Request:** The request is malformed. Check that the JSON is valid and that all required fields are present.
- **500 Internal Server Error:** There is a problem with the server. Check the server logs for more details.
- **503 Service Unavailable:** The service is temporarily unavailable. This may happen if the assistant is not yet initialized.

If you encounter any issues, please check the server logs for detailed error messages.

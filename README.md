# Flask Solidarity Checker

This Flask application provides a service to verify the identity of a caller by comparing the name associated with a phone number from Twilio's Lookup API with a name from a database (either a local mock database or the Solidarity Tech API).

## Features

*   **Phone Number Lookup:** Get the caller name for a given phone number using Twilio's Lookup API.
*   **Identity Verification:** Verify a caller's identity by comparing the name from Twilio with a name from a database.
*   **Bulk Identity Verification:** Verify the identities of all users in the database.
*   **Mock API:** Includes a mock Solidarity Tech API for testing purposes.
*   **Flexible Database:** Can use either a local mock database or the Solidarity Tech API.
*   **Lookup Cache:** Recent lookups are cached in a local SQLite database to reduce Twilio API calls.
*   **Dockerized:** Comes with a `Dockerfile` for easy deployment.

## Setup and Installation

There are two ways to run this application: using Docker (recommended) or running it directly on your machine.

### Running with Docker (Recommended)

Using Docker is the easiest way to get the application running.

**Prerequisites:**

*   [Docker](https://docs.docker.com/get-docker/)

**Steps:**

1.  **Clone the repository (optional):**
    ```bash
    git clone <repository_url>
    cd flask-solidarity-checker
    ```

2.  **Configure environment variables:**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    SOLIDARITY_TECH_API_KEY=your_solidarity_tech_api_key
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    CACHE_TTL_SECONDS=3600
    ```

    *   `SOLIDARITY_TECH_API_KEY`: Your API key for the Solidarity Tech API. If you don't have one, the application will use a local mock database.
    *   `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`: Your Twilio Account SID and Auth Token. You can find these on your [Twilio Console](https://www.twilio.com/console).
    *   `CACHE_TTL_SECONDS` (optional): How long, in seconds, to store lookup results in the cache (default: 3600).

3.  **Build and run the Docker container:**

    ```bash
    docker build -t solidarity-checker .
    docker run -p 5000:5000 --env-file .env solidarity-checker
    ```

The application will be available at `http://127.0.0.1:5000`.

### Running Locally

**Prerequisites:**

*   Python 3.6+
*   pip

**Steps:**

1.  **Clone the repository (optional):**
    ```bash
    git clone <repository_url>
    cd flask-solidarity-checker
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure environment variables:**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    SOLIDARITY_TECH_API_KEY=your_solidarity_tech_api_key
    TWILIO_ACCOUNT_SID=your_twilio_account_sid
    TWILIO_AUTH_TOKEN=your_twilio_auth_token
    CACHE_TTL_SECONDS=3600
    ```

    *   `SOLIDARITY_TECH_API_KEY`: Your API key for the Solidarity Tech API. If you don't have one, the application will use a local mock database.
    *   `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN`: Your Twilio Account SID and Auth Token. You can find these on your [Twilio Console](https://www.twilio.com/console).
    *   `CACHE_TTL_SECONDS` (optional): How long, in seconds, to store lookup results in the cache (default: 3600).

4.  **Run the application:**

    ```bash
    python app.py
    ```

The application will be available at `http://127.0.0.1:5000`.

## API Endpoints

### Lookup Phone Number

*   **GET** `/lookup`

    Retrieves the caller name for a given phone number from Twilio.

    **Query Parameters:**

    *   `phone_number` (string, required): The phone number to look up (e.g., `+15551234567`).

    **Example Response:**

    ```json
    {
        "phone_number": "+15551234567",
        "name": "John Doe"
    }
    ```

### Verify Identity

*   **GET** `/verify_identity`

    Verifies the identity of a caller by comparing the name from Twilio with the name in the database.

    **Query Parameters:**

    *   `phone_number` (string, required): The phone number to verify.

    **Example Response:**

    ```json
    {
        "status": "Identity Verified"
    }
    ```

### Verify All Identities

*   **GET** `/verify_all_identities`

    Verifies the identities of all users in the database.

    **Example Response:**

    ```json
    [
        {
            "phone_number": "+15551234567",
            "claimed_name": "John Doe",
            "twilio_name": "John Doe",
            "status": "Identity Verified"
        },
        {
            "phone_number": "+15557654321",
            "claimed_name": "Jane Smith",
            "twilio_name": "Jane Smith",
            "status": "Identity Verified"
        }
    ]
    ```

### Get Caller Name

*   **GET** `/get_caller_name`

    Retrieves the last looked-up caller name.

    **Example Response:**

    ```json
    {
        "caller_name": "John Doe"
    }
    ```

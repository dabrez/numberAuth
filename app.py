# Import necessary libraries
import os
from flask import Flask, request, jsonify
from twilio.rest import Client
import requests
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Get Twilio and Solidarity Tech API credentials from environment variables
# Your Account SID and Auth Token from twilio.com/console
account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
solidarity_tech_api_key = os.environ.get("SOLIDARITY_TECH_API_KEY")

# Check if Twilio credentials are set
if not account_sid or not auth_token:
    print("WARNING: TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables are not set.")
    print("Please set them to use the Twilio Lookup API.")
    # For demonstration purposes, we'll allow the app to run without them,
    # but the lookup functionality will fail.

# Initialize the Twilio client
client = Client(account_sid, auth_token)

# Global variable to store the last looked-up caller name
stored_caller_name = None

# A local mock database of phone numbers and names.
# This is used as a fallback if the Solidarity Tech API key is not provided.
local_mock_database = {
    "+15551234567": "John Doe",
    "+15557654321": "Jane Smith"
}

# This route simulates the Solidarity Tech API.
# It returns a static list of users.
@app.route("/solidarity_tech_api/users", methods=["GET"])
def get_users():
    """Mock Solidarity Tech API endpoint to get a list of users."""
    users = [
        {
            "phone_number": "+15551234567",
            "name": "John Doe"
        },
        {
            "phone_number": "+15557654321",
            "name": "Jane Smith"
        }
    ]
    return jsonify(users)

# This route looks up the caller name for a given phone number using the Twilio Lookup API.
@app.route("/lookup", methods=["GET"])
def lookup_phone_number():
    """
    Looks up the caller name for a given phone number using the Twilio Lookup API.
    The phone number should be passed as a query parameter.
    Example: /lookup?phone_number=+15551234567
    """
    global stored_caller_name
    phone_number = request.args.get("phone_number")

    # Check if the phone_number parameter is provided
    if not phone_number:
        return jsonify({"error": "phone_number parameter is required"}), 400

    try:
        # Use the Twilio Lookup API v2 to fetch the caller name.
        # Note: Caller Name lookup is primarily available for US numbers and is a paid feature.
        # Ensure your Twilio account has Caller Name enabled and sufficient balance.
        phone_number_info = client.lookups.v2.phone_numbers(phone_number).fetch(fields="caller_name")
        caller_name = phone_number_info.caller_name
        stored_caller_name = caller_name  # Store the caller name in the global variable

        # Return the caller name if found
        if caller_name:
            return jsonify({"phone_number": phone_number, "name": caller_name}), 200
        else:
            return jsonify({"phone_number": phone_number, "name": "Name not found or not available"}), 200
    except Exception as e:
        # Handle exceptions, such as an invalid phone number
        return jsonify({"error": str(e)}), 500

# This route retrieves the last looked-up caller name.
@app.route("/get_caller_name", methods=["GET"])
def get_caller_name():
    """Retrieves the last looked-up caller name."""
    if stored_caller_name:
        return jsonify({"caller_name": stored_caller_name}), 200
    else:
        return jsonify({"message": "Caller name not found or not looked up yet."}), 404

# This route verifies the identity of a caller by comparing the name from Twilio with the name in the database.
@app.route("/verify_identity", methods=["GET"])
def verify_identity():
    """
    Verifies the identity of a caller by comparing the name from the Twilio Lookup API
    with the name in the database (either Solidarity Tech API or local mock database).
    The phone number should be passed as a query parameter.
    Example: /verify_identity?phone_number=+15551234567
    """
    phone_number = request.args.get("phone_number")

    # Check if the phone_number parameter is provided
    if not phone_number:
        return jsonify({"error": "phone_number parameter is required"}), 400

    user_data = {}
    # If a Solidarity Tech API key is provided, use the API to get user data
    if solidarity_tech_api_key:
        try:
            response = requests.get("http://127.0.0.1:5000/solidarity_tech_api/users")
            response.raise_for_status()  # Raise an exception for bad status codes
            users = response.json()
            user_data = {user["phone_number"]: user["name"] for user in users}
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Could not connect to Solidarity Tech API: {e}"}), 500
    else:
        # Otherwise, use the local mock database
        user_data = local_mock_database

    # Get the claimed name from the database
    claimed_name = user_data.get(phone_number)

    # Check if the phone number is in the database
    if not claimed_name:
        return jsonify({"error": "Phone number not found in database"}), 404

    # Get the caller name from the Twilio lookup
    try:
        phone_number_info = client.lookups.v2.phone_numbers(phone_number).fetch(fields="caller_name")
        caller_name = phone_number_info.caller_name
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Compare the name from Twilio with the name from the database
    if caller_name and caller_name == claimed_name:
        return jsonify({"status": "Identity Verified"}), 200
    else:
        return jsonify({"status": "Identity Invalid"}), 200

# This route verifies the identities of all users in the database.
@app.route("/verify_all_identities", methods=["GET"])
def verify_all_identities():
    """
    Verifies the identities of all users in the database by comparing the names
    from the Twilio Lookup API with the names in the database.
    """
    user_data = {}
    # If a Solidarity Tech API key is provided, use the API to get user data
    if solidarity_tech_api_key:
        try:
            response = requests.get("http://127.0.0.1:5000/solidarity_tech_api/users")
            response.raise_for_status()  # Raise an exception for bad status codes
            users = response.json()
            user_data = {user["phone_number"]: user["name"] for user in users}
        except requests.exceptions.RequestException as e:
            return jsonify({"error": f"Could not connect to Solidarity Tech API: {e}"}), 500
    else:
        # Otherwise, use the local mock database
        user_data = local_mock_database

    results = []
    # Iterate over all users in the database
    for phone_number, claimed_name in user_data.items():
        try:
            # Get the caller name from the Twilio lookup
            phone_number_info = client.lookups.v2.phone_numbers(phone_number).fetch(fields="caller_name")
            caller_name = phone_number_info.caller_name
        except Exception as e:
            # Handle exceptions, such as an invalid phone number
            results.append({
                "phone_number": phone_number,
                "claimed_name": claimed_name,
                "twilio_name": None,
                "status": "Twilio Lookup Error",
                "error": str(e)
            })
            continue

        # Compare the names
        if caller_name and caller_name == claimed_name:
            status = "Identity Verified"
        else:
            status = "Identity Invalid"
        
        results.append({
            "phone_number": phone_number,
            "claimed_name": claimed_name,
            "twilio_name": caller_name or "Name not found or not available",
            "status": status
        })

    return jsonify(results)

# This block runs the Flask application.
if __name__ == "__main__":
    # The app is run in debug mode, which provides helpful error messages.
    # The host is set to "0.0.0.0" to make the app accessible from other devices on the same network.
    app.run(debug=True, host="0.0.0.0", port=5000)

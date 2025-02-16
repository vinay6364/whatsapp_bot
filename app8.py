from flask import Flask, request, session
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "5f4dcc3b5aa765d61d8327deb882cf99f4dcc3b5aa765d61")  # Use environment variable for secret key

@app.route("/webhook", methods=['POST'])
def webhook():
    # Get the incoming message from the user
    incoming_msg = request.form.get('Body', '').strip().lower()
    user_number = request.form.get("From", "")
    response = MessagingResponse()

    # Initialize session for users if it doesn't exist
    if "users" not in session:
        session["users"] = {}

    # Handle new users
    if user_number not in session["users"]:
        if incoming_msg == "start":
            session["users"][user_number] = {"name": None, "menu_shown": False}
            response.message("Welcome to our chatbot! Before we start, what's your name?")
            return str(response)
        else:
            response.message("Please type 'start' to begin.")
            return str(response)

    # Get user data from session
    user_data = session["users"].get(user_number, {})

    # Handle name input
    if user_data.get("name") is None:
        session["users"][user_number]["name"] = incoming_msg.capitalize()
        response.message(f"Hello {incoming_msg.capitalize()}! Nice to meet you. Please choose an option below:\n1. Startup\n2. Call\n3. Msg\n4. Exit\n5. Restart")
        session["users"][user_number]["menu_shown"] = True
        return str(response)

    # Handle menu options
    if user_data.get("menu_shown"):
        if incoming_msg in ["1", "startup"]:
            response.message("Thank you for choosing Startup.\nThis feature is still in the developmental phase.")
        elif incoming_msg in ["2", "call"]:
            response.message("Thank you for choosing Call.\nThis feature is still in the developmental phase.")
        elif incoming_msg in ["3", "msg"]:
            response.message("Thank you for choosing Msg.\nThis feature is still in the developmental phase.")
        elif incoming_msg in ["4", "exit"]:
            response.message("Thank you for your time. Welcome back anytime!")
            session["users"].pop(user_number, None)  # End the session completely
            return str(response)
        elif incoming_msg in ["5", "restart"]:
            session["users"].pop(user_number, None)  # Restart session for this user
            response.message("Restarting session...\nPlease type 'start' to begin again.")
            return str(response)
        else:
            response.message("Invalid choice. Please select from:\n1. Startup\n2. Call\n3. Msg\n4. Exit\n5. Restart")
            return str(response)

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's PORT or default to 5000
    app.run(host="0.0.0.0", port=port, debug=False)  # Set debug=False for production

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Track user sessions and data
user_sessions = {}

# Menu options
MENU_OPTIONS = (
    "Please choose an option by typing the number:\n"
    "1. Areka nut plantation\n"
    "2. Apiary\n"
    "3. Nursery kit\n"
    "4. Seedling kit\n"
    "5. Honey products\n"
    "6. Exit\n"
    "7. Restart\n"
)

# Twilio webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook():
    # Get the incoming message from WhatsApp
    incoming_message = request.form.get("Body", "").strip().lower()
    sender = request.form.get("From", "")

    print(f"Received message from {sender}: {incoming_message}")

    # Initialize Twilio response object
    twilio_response = MessagingResponse()

    # Retrieve or initialize user session safely
    user_data = user_sessions.get(sender, {"step": None, "name": "", "location": ""})

    # Check if the user is starting the conversation
    if incoming_message == "start":
        welcome_message = (
            "\U0001F44B Hello! Welcome to the chatbot. I'm here to help you.\n"
            "What's your name?"
        )
        twilio_response.message(welcome_message)
        user_sessions[sender] = {"step": "ask_name", "name": "", "location": ""}
    elif user_data.get("step") == "ask_name":
        user_data["name"] = incoming_message
        user_data["step"] = "ask_location"
        twilio_response.message(f"Nice to meet you, {incoming_message}! Where are you from?")
        user_sessions[sender] = user_data
    elif user_data.get("step") == "ask_location":
        user_data["location"] = incoming_message
        user_data["step"] = "show_menu"
        twilio_response.message(
            f"Got it, {user_data['name']} from {incoming_message}!\n\n"
            f"{MENU_OPTIONS}"
        )
        user_sessions[sender] = user_data
    elif user_data.get("step") == "show_menu":
        if incoming_message in ["1", "2", "3", "4", "5", "7"]:
            twilio_response.message(
                "This feature is still in the developmental phase. "
                "You can contact this number for further assistance: 1233455."
            )
            user_data["step"] = "completed"
            user_sessions[sender] = user_data
        elif incoming_message == "6":
            twilio_response.message("Farewell! Come back anytime. \U0001F44B")
            user_sessions.pop(sender, None)
        else:
            twilio_response.message("Invalid option. Please choose a number from 1 to 7.")
            twilio_response.message(MENU_OPTIONS)
    elif user_data.get("step") == "completed":
        if "thank you" in incoming_message:
            twilio_response.message("Thank you for choosing Areka Karmik Private Limited!")
        else:
            twilio_response.message("I'm here to assist you. Please type 'start' if you need help.")
    else:
        twilio_response.message("Please type 'start' to begin the conversation.")

    return str(twilio_response)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)  # Set debug=False in production

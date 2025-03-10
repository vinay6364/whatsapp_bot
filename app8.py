from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Initialize the chatbot
chatbot = ChatBot('WhatsAppBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")  # Train on English corpus

# Track user sessions and data
user_sessions = {}

# URL of the animated honey bee image (replace with your actual image URL)
HONEY_BEE_IMAGE_URL = "https://example.com/honey-bee.gif"  # Replace with a valid URL

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

    # Retrieve or initialize user session
    user_data = user_sessions.get(sender, {"step": None})

    # Check if the user is starting the conversation
    if incoming_message == "start":
        # Send a welcome message and ask for the user's name
        welcome_message = (
            "👋 Hello! Welcome to the chatbot. I'm here to help you.\n"
            "What's your name?"
        )
        twilio_response.message(welcome_message)
        # Initialize user session
        user_sessions[sender] = {"step": "ask_name"}
    elif user_data["step"] == "ask_name":
        # Save the user's name and ask for their location
        user_data["name"] = incoming_message
        user_data["step"] = "ask_location"
        twilio_response.message(f"Nice to meet you, {incoming_message}! Where are you from?")
        user_sessions[sender] = user_data  # Update session
    elif user_data["step"] == "ask_location":
        # Save the user's location and confirm
        user_data["location"] = incoming_message
        user_data["step"] = "show_menu"
        twilio_response.message(
            f"Got it, {user_data['name']} from {incoming_message}!\n\n"
            f"{MENU_OPTIONS}"
        )
        user_sessions[sender] = user_data  # Update session
    elif user_data["step"] == "show_menu":
        # Handle menu options
        if incoming_message in ["1", "2", "3", "4", "5", "7"]:
            # Respond with developmental phase message
            twilio_response.message(
                "This feature is still in the developmental phase. "
                "You can contact this number for further assistance: 1233455."
            )
            user_data["step"] = "completed"  # Set step to completed
            user_sessions[sender] = user_data  # Update session
        elif incoming_message == "6":
            # End the session with a farewell message
            twilio_response.message("Farewell! Come back anytime. 👋")
            # Clear the user's session
            user_sessions.pop(sender, None)
        else:
            # Handle invalid input
            twilio_response.message("Invalid option. Please choose a number from 1 to 7.")
            twilio_response.message(MENU_OPTIONS)  # Re-prompt with menu options
    elif user_data["step"] == "completed":
        # Handle normal conversation
        if "thank you" in incoming_message:
            # Send the honey bee image and thank you message
            msg = twilio_response.message("Thank you for choosing Areka Karmik Private Limited!")
            msg.media(HONEY_BEE_IMAGE_URL)
        else:
            # Default chatbot response
            try:
                response = chatbot.get_response(incoming_message)
                twilio_response.message(str(response))
            except Exception as e:
                twilio_response.message("Sorry, I encountered an error. Please try again.")
                print(f"Error generating chatbot response: {e}")
    else:
        # If the user hasn't started the conversation, prompt them to type 'start'
        twilio_response.message("Please type 'start' to begin the conversation.")

    return str(twilio_response)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)  # Set debug=False in production

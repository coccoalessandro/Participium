from __future__ import annotations

from participium.services.messaging_service import MessagingService

# Function: 
# Inputs: report(Report), sender(User), body(str)
# Expected Output:
# - The persisted `Message` if the message is sent successfully.
# - AuthorizationError if the sender cannot access the thread.
# - ValidationError if the body is empty or blank after trimming.
# - ValidationError if no recipient can currently be resolved for the conversation.
#def send_message(self, report: Report, sender: User, body: str) -> Message



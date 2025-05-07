from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import os
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file at module level
load_dotenv()

class SendSmsToolInput(BaseModel):
    """Input schema for SendSmsToContact."""
    message: str = Field(..., description="The message to send to the contact")

class SendSmsToContact(BaseTool):
    args_schema: Type[BaseModel] = SendSmsToolInput
    name: str = "Send SMS to {contact_name}"
    description: str = "Sends an SMS message using Twilio"

    # Declare the fields that will be set in __init__
    from_number: str = Field(..., description="The Twilio phone number to send from")
    to_number: str = Field(..., description="The recipient's phone number")
    contact_name: str = Field(..., description="The name of the contact")

    def __init__(self, from_number: str, to_number: str, contact_name: str):
        """Initialize the SMS tool with contact details.

        Args:
            from_number: The Twilio phone number to send from
            to_number: The recipient's phone number
            contact_name: The name of the contact (used in tool name/description)
        """
        super().__init__(
            from_number=from_number,
            to_number=to_number,
            contact_name=contact_name
        )
        self.name = self.name.format(contact_name=contact_name)

    def _run(self, message: str) -> str:
        """Send an SMS message using Twilio.

        Args:
            message: The message to send

        Returns:
            str: A status message indicating success or failure
        """
        try:
            # Get Twilio credentials from environment variables
            account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
            api_key = os.environ.get('TWILIO_API_KEY')
            api_secret = os.environ.get('TWILIO_API_KEY_SECRET')

            if not all([account_sid, api_key, api_secret]):
                missing = [k for k, v in {
                    'TWILIO_ACCOUNT_SID': account_sid,
                    'TWILIO_API_KEY': api_key,
                    'TWILIO_API_KEY_SECRET': api_secret
                }.items() if not v]
                return f"Error: Missing Twilio credentials: {', '.join(missing)}"

            print(f"Using Account SID: {account_sid}")  # Debug log

            # Initialize Twilio client with API Key authentication
            client = Client(api_key, api_secret, account_sid)

            # Send message
            message = client.messages.create(
                body=message,
                from_=self.from_number,
                to=self.to_number
            )

            return f"Message sent successfully to {self.contact_name}. Message SID: {message.sid}"

        except Exception as e:
            return f"Error sending message to {self.contact_name}: {str(e)}"

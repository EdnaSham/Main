import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# to authenticate requests to Google Calendar API
#Google_Calendar_API_Key = os.getenv('Google_Calendar_API_Key')
#Google_Calendar_Base_API_URL = "https://www.googleapis.com/calendar/v3"

# Scopes required for the Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Path to your credentials file
CLIENT_SECRET_FILE = 'C:/Users/esham/OneDrive/Documents/Coding/Mental_Health/client_secret.json'

# Environment settings
ENVIRONMENT = "test"

# raise an error if the environment variables are not set
#if not Google_Calendar_API_Key:
 #  raise EnvironmentError("API keys are not set in environment variables")

# Use the API keys in your application
#print(f"Google_Calendar_API_Key: {Google_Calendar_API_Key}")
#print(Google_Calendar_Base_API_URL)
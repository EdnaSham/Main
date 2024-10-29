import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# to authenticate requests to Hugging Face API
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')

#to authenticate requests to the JSM API
JSM_Frontend_API_Base_URL = "https://eshamouni.atlassian.net/rest/servicedeskapi/"
JSM_Backend_API_Base_URL = "https://eshamouni.atlassian.net/rest/api/3/issue"
JSM_API_KEY = os.getenv('JSM_API_KEY')
JIRA_PROJECT_KEY = "SDCP"
JIRA_ISSUE_TYPE_ID = "10005" # for Support issue type, ID number found by  inspecting the element on the web page.


# Other configurations
CHATBOT_NAME = "ServiceDeskBot"
EMAIL = "e.shamouni@gmail.com"
WELCOME_MESSAGE = "Hello! I'm ServiceDeskBot. How can I assist you today?"
TIMEOUT_SECONDS = 60
ERROR_RESPONSE = "I'm sorry, I couldn't process your request at the moment. Please try again later."

# Environment settings
ENVIRONMENT = "development"

# raise an error if the environment variables are not set
if not HUGGINGFACE_API_KEY or not JSM_API_KEY:
    raise EnvironmentError("API keys are not set in environment variables")

# Use the API keys in your application
# print(f"HUGGINGFACE_API_KEY: {HUGGINGFACE_API_KEY}")
# print(f"JSM_API_KEY: {JSM_API_KEY}")
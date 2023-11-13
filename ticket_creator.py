import os 
from dotenv import load_dotenv
load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY')
print('testing')


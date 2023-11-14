import os 
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY')
email = os.getenv('JIRA_EMAIL')
jira_server = os.getenv('JIRA_SERVER')
jiraOptions = {'server': jira_server }

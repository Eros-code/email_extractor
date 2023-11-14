import os 
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY')
jira_email = os.getenv('JIRA_EMAIL')
jira_server = os.getenv('JIRA_SERVER')
jiraOptions = {'server': jira_server } #

jira = JIRA(options=jiraOptions, basic_auth=(jira_email, jira_auth_key))


for singleIssue in jira.search_issues(jql_str='project = TJIC'):
    print('{}: {}:{}'.format(singleIssue.key, singleIssue.fields.summary,singleIssue.fields.reporter.displayName))
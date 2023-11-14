import os 
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY') #Jira api key
jira_email = os.getenv('JIRA_EMAIL') #email used for Jira account
jira_server = os.getenv('JIRA_SERVER') # Jira board URL, looks like ______.atlassian.net
jiraOptions = {'server': jira_server } #

jira = JIRA(options=jiraOptions, basic_auth=(jira_email, jira_auth_key))


for singleIssue in jira.search_issues(jql_str='project = TJIC'):
    print('{}: {}:{}'.format(singleIssue.key, singleIssue.fields.summary,singleIssue.fields.reporter.displayName))



def create_new_issue():
    new_issue = jira.create_issue(project='TJIC', summary='New issue from jira-python',
                                description='Look into this one', issuetype={'name': 'Bug'})

create_new_issue()
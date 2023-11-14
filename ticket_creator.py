import os 
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY') #Jira api key
jira_email = os.getenv('JIRA_EMAIL') #email used for Jira account
jira_server = os.getenv('JIRA_SERVER') # Jira board URL, looks like ______.atlassian.net
jiraOptions = {'server': jira_server } 


def connect_to_jira():
    jira = JIRA(options=jiraOptions, basic_auth=(jira_email, jira_auth_key))
    return jira

def create_new_issue(project_name, issue_summary, issue_description, issue_type = 'Task'):
    new_issue = jira.create_issue(project = project_name, summary = issue_summary,
                                description = issue_description, issuetype={'name': issue_type})
    
def list_all_issues(project_name):
    for singleIssue in jira.search_issues(jql_str = f'project = {project_name}'):
        print('{}: {}:{}'.format(singleIssue.key, singleIssue.fields.summary,singleIssue.fields.reporter.displayName))


if __name__=='__main__':
    jira = connect_to_jira()

    project_name = 'TJIC'
    issue_summary = 'work hard'
    issue_description = 'work harder'
    
    create_new_issue(project_name, issue_summary, issue_description)
    list_all_issues(project_name)
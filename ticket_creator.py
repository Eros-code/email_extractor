import os 
from datetime import datetime
from dotenv import load_dotenv
from jira import JIRA

load_dotenv()
jira_auth_key = os.getenv('JIRA_AUTH_KEY') #Jira api key
jira_email = os.getenv('JIRA_EMAIL') #email used for Jira account
jira_server = os.getenv('JIRA_SERVER') # Jira board URL, looks like ______.atlassian.net
jiraOptions = {'server': jira_server } 


def connect_to_jira(jiraOptions, jira_email, jira_auth_key):
    try:
        jira = JIRA(options=jiraOptions, basic_auth=(jira_email, jira_auth_key))
        print({'Response':"connected to jira board successfully"})
        return jira
    except:
        print({'Response':"could not connect to Jira board"})

def create_new_issue(jira, project_name, issue_summary, issue_description, issue_type = 'Task'):
    new_issue = jira.create_issue(project = project_name, summary = issue_summary,
                                description = issue_description, issuetype={'name': issue_type})
    
def list_all_issues(jira, project_name):
    issue_list = []
    for singleIssue in jira.search_issues(jql_str = f'project = {project_name}'):
        issue_list.append({f'{singleIssue.key}' : {'summary' : singleIssue.fields.summary, 'displayName': singleIssue.fields.reporter.displayName, 'description': singleIssue.fields.description}})
    return issue_list


if __name__=='__main__':
    jira = connect_to_jira(jiraOptions, jira_email, jira_auth_key)

    project_name = 'TK'
    issue_summary = 'work hard'
    issue_description = 'work harder'
    
    create_new_issue(jira, project_name, issue_summary, issue_description)
    list_all_issues(jira, project_name)
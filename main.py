# To get started, we don't have to install anything. All the modules used in this tutorial are the built-in ones:

import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from dotenv import load_dotenv
import re
from ticket_creator import connect_to_jira, list_all_issues, create_new_issue
from read_data_domains import read_yaml_from_github, find_data_domains

# import jira library after doing pip install jira
from jira.client import JIRA

# first go here: https://id.atlassian.com/manage-profile/security/api-tokens
# to generate an api token for your account - this needs to be securely stored
# for now lets put it in the .env file so no one can access it

# Load the dotenv file
load_dotenv()

# account credentials
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
api_token = os.getenv('JIRA_API')
jiraServer = os.getenv('JIRA_SERVER')
jiraEmail = os.getenv('JIRA_EMAIL')
access_token = os.getenv('access_token')

# use your email provider's IMAP server, you can look for your provider's IMAP server on Google
# or check this page: https://www.systoolsgroup.com/imap/
# for office 365, it's this:
imap_server = "outlook.office365.com"

matches = ["ACTION:", 
                   "EMAIL:",
                   "DASHBOARD_NAME(S):",
                   "TEAM:",
                   "SC END DATE:",
                   "SC STATUS:",
                   "AUDIT SOURCE(S):",
                   "SERVICE(S):",
                   "USER TO COPY EMAIL:"]

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def retrieveEmailMessages(messages, N):
    emailList = []
    for i in range(messages, messages-N, -1):
        emailDictionary = {}
    # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
        res, uid = imap.fetch(str(i), "uid")
        
        print(uid)
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode('utf-8')
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)

                emailDictionary['Subject'] = subject
                emailDictionary['From'] = From
                emailDictionary['Date'] = msg['date']
                emailDictionary['uid'] = uid[0].decode('utf-8')[-2]
                print(emailDictionary['uid'])

                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            emailDictionary['body'] = body
                            emailDictionary['attachment'] = 'No'
                        elif "attachment" in content_disposition:
                            emailDictionary['attachment'] = 'Yes'
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        emailDictionary['body'] = body
                        emailDictionary['attachment'] = 'No'
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    pass
        emailList.append(emailDictionary)
    # close the connection and logout


    return emailList

def templateChecker(retrievedEmails, variable):
    retrievedEmailBodies = []
    for retrievedEmail in retrievedEmails:
        print(retrievedEmail)
        if all(variable in retrievedEmail['body'] for variable in matches):
            retrievedEmailBodies.append({'body' : retrievedEmail['body'], 'uid' : retrievedEmail['uid']})
        else:
            pass

   
    return retrievedEmailBodies

def moveTemplateEmail(retrievedEmails, imap):
    for retrievedEmail in retrievedEmails:
        # imap.copy([b'3 (UID 5)'], 'imap_test/imap_processed')
        imap.uid('MOVE', retrievedEmail['uid'], 'imap_processed')


def templateVariableSeparator(emailOutputs):
    emailOutputVariables = []
    for emailOutput in emailOutputs:
        
        variablesDict = {}
        for i in range(len(matches)-1):
            matchIndex = emailOutput['body'].find(matches[i])+len(matches[i])
            matchIndexAfter = emailOutput['body'].find(matches[i+1])
            variablesDict[matches[i][:-1]] = emailOutput['body'][matchIndex:matchIndexAfter]
            variablesDict[matches[i][:-1]] = variablesDict[matches[i][:-1]].replace("\r\n", " ")
            variablesDict[matches[i][:-1]] = variablesDict[matches[i][:-1]].strip()
        
        matchIndex = emailOutput['body'].find(matches[-1])+len(matches[-1])
        matchIndexAfter = emailOutput['body'][matchIndex:].index('%')
        UserCopy = emailOutput['body'][matchIndex:]
        variablesDict[matches[-1][:-1]] = UserCopy[:matchIndexAfter]
        variablesDict[matches[-1][:-1]] = variablesDict[matches[-1][:-1]].replace("\r\n", " ")
        variablesDict[matches[-1][:-1]] = variablesDict[matches[-1][:-1]].strip()

        emailOutputVariables.append(variablesDict)
    
    return emailOutputVariables
        


# We've imported the necessary modules and then specified the credentials of our email account. 

if __name__=='__main__':
    # First, we gonna need to connect to the IMAP server:

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)

    # try:
    # authenticate
    imap.login(username, password)
    print('login to outlook email account was successful')

    status, messages = imap.select("imap_test")
    # number of top emails to fetch
    N = 3
    # total number of emails
    messages = int(messages[0])
    # We've used the imap.select() method, which selects a mailbox (Inbox, spam, etc.), we've chosen the INBOX folder. You can use the imap.list() method to see the available mailboxes.
    retrievedEmail = retrieveEmailMessages(messages, N)
    emailOutput = templateChecker(retrievedEmail, matches)
    moveTemplateEmail(emailOutput, imap)
    
    variables = templateVariableSeparator(emailOutput)
    yaml_data = read_yaml_from_github(access_token)
    try:
        jiraOptions = {'server': jiraServer}
        projectName = 'TJIC'
        
        jira = connect_to_jira(jiraOptions, jiraEmail, api_token)

        for variable in variables:
            ticket_summary = ''
            new_data_domains, missing_audit_sources = find_data_domains(yaml_data, variable['AUDIT SOURCE(S)'])
            
            # if the service the user has entered doesnt correspond
            # to captured data domains then exclude from final list

            services = variable['SERVICE(S)'].split(';')
            data_domain_checker = []
            for domain in new_data_domains:
                if any(service in domain for service in services):
                    data_domain_checker.append(domain)

            new_audit_source_value = ';'.join(data_domain_checker)

            variable['AUDIT SOURCE(S)'] = new_audit_source_value
            variable['MISSING AUDIT SOURCE(S)'] = missing_audit_sources

            print(variable)

            # for key, value in retrievedEmail.items():
            #     if key != 'body':
            #         ticket_summary += f"{key}: {value}\n"
            # ticket_summary += '\n'

            for key, value in variable.items():
                ticket_summary += f"{key}: {value}\n"

            # create_new_issue(jira, projectName, 'onboarding 22', ticket_summary)
            
    except Exception as e:
        print('failed', e)


    imap.close()
    imap.logout()
    # print(list_all_issues(jira, projectName))
    
    # #Get one story and print out some stuff to show it worked
    # issue = jira.issue(id='TK-8')
    # print(issue.fields.description)

        
    # except:
    #     print('login to outlook email account was not successful')

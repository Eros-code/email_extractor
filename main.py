# To get started, we don't have to install anything. All the modules used in this tutorial are the built-in ones:

import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from dotenv import load_dotenv
import re

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
api_token = os.getenv('JIRA-API')
jiraServer = os.getenv('JIRA-SERVER')
jiraEmail = os.getenv('JIRA-EMAIL')

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
                   "AUDIT SOURCE:",
                   "USER_TO_COPY_EMAIL:"]

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def retrieveEmailMessages(messages, N):
    emailList = []
    for i in range(messages, messages-N, -1):
        emailDictionary = {}
    # fetch the email message by ID
        res, msg = imap.fetch(str(i), "(RFC822)")
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
    imap.close()
    imap.logout()

    return emailList

def templateChecker(retrievedEmail):
    if all(variable in retrievedEmail['body'] for variable in matches):
        return retrievedEmail['body']
    else:
        return 'template not detected'
    
def templateVariableSeparator(emailOutput):
    if emailOutput != 'template not detected':
        variablesDict = {}
        for i in range(len(matches)-1):
            matchIndex = emailOutput.find(matches[i])+len(matches[i])
            matchIndexAfter = emailOutput.find(matches[i+1])
            variablesDict[matches[i][:-1]] = emailOutput[matchIndex:matchIndexAfter]
            variablesDict[matches[i][:-1]] = variablesDict[matches[i][:-1]].replace("\r\n", " ")
            variablesDict[matches[i][:-1]] = variablesDict[matches[i][:-1]].strip()
        
        matchIndex = emailOutput.find(matches[-1])+len(matches[-1])
        matchIndexAfter = emailOutput[matchIndex:].index('%')
        UserCopy = emailOutput[matchIndex:]
        variablesDict[matches[-1][:-1]] = UserCopy[:matchIndexAfter]
        variablesDict[matches[-1][:-1]] = variablesDict[matches[-1][:-1]].replace("\r\n", " ")
        variablesDict[matches[-1][:-1]] = variablesDict[matches[-1][:-1]].strip()
        return variablesDict
    else:
         return {'Response': emailOutput}
    
def jiraBoardConnector():
    # Construct a Client-instance that will request your required data from the Jira server. This will require the Server name (to which the client will send its data request) given by your Domain name. 
    try:
        jiraOptions = {'server': jiraServer}
        jira = JIRA(options=jiraOptions, basic_auth=(f"{jiraEmail}", f"{api_token}"))
        print ({'Response': 'successfully connected to jira account'})
        return jira
    except:
        print ({'Response': 'could not connect to jira account'})

# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import requests
from requests.auth import HTTPBasicAuth
import json
 
def JiraBoard():
    url = jiraServer + '/rest/api/3/search'
    
    auth = HTTPBasicAuth(jiraEmail, api_token)
    
    headers = {
        "Accept": "application/json"
    }
    
    query = {
        'jql': 'key = TK-1'
    }
    
    response = requests.request(
        "GET",
        url,
        headers=headers,
        params=query,
        auth=auth
    )
    
    data = json.loads(response.text)
    selectedIssues=[]
    #Get all issues and put them into an array
    print(data)


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
    retrievedEmail = retrieveEmailMessages(messages, N)[0]
    emailOutput = templateChecker(retrievedEmail)
    variables = templateVariableSeparator(emailOutput)

    print(variables)

    # jira = jiraBoardConnector()
    
    # #Get one story and print out some stuff to show it worked
    # issue = jira.issue(id='TK-1')

    JiraBoard()

        
    # except:
    #     print('login to outlook email account was not successful')

# To get started, we don't have to install anything. All the modules used in this tutorial are the built-in ones:

import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from dotenv import load_dotenv
import re

# Load the dotenv file
load_dotenv()

# account credentials
username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
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
    

# We've imported the necessary modules and then specified the credentials of our email account. 

if __name__=='__main__':
    # First, we gonna need to connect to the IMAP server:

    # create an IMAP4 class with SSL 
    imap = imaplib.IMAP4_SSL(imap_server)

    try:
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


            print(variablesDict)


        else:
            print(emailOutput)

        
    except:
        print('login to outlook email account was not successful')

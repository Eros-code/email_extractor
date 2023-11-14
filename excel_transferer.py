from ticket_creator import connect_to_jira
from dotenv import load_dotenv
from main import templateVariableSeparator
import os
import numpy as np

# pip install google_spreadsheet
# pip install google-auth-oauthlib
# pip install pandas

# Enable the Google sheet API.
# Go to https://developers.google.com/sheets/api/quickstart/python.



matches = ["ACTION:", 
                   "EMAIL:",
                   "DASHBOARD_NAME(S):",
                   "TEAM:",
                   "SC END DATE:",
                   "SC STATUS:",
                   "AUDIT SOURCE:",
                   "USER_TO_COPY_EMAIL:"]

load_dotenv()
jira_auth_key = os.getenv('JIRA_API') #Jira api key
jira_email = os.getenv('JIRA_EMAIL') #email used for Jira account
jira_server = os.getenv('JIRA_SERVER') # Jira board URL, looks like ______.atlassian.net
jiraOptions = {'server': jira_server }
SAMPLE_SPREADSHEET_ID_input = os.getenv('GOOGLE_SHEET')


import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow,Flow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SAMPLE_RANGE_NAME = 'A1:AA1000'

def api_call():
    global values_input, service
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])

    if not values_input and not values_expansion:
        print('No data found.')

def Create_Service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        #return service
    except Exception as e:
        print(e)
        #return None
        
# change 'my_json_file.json' by your downloaded JSON file.
Create_Service('credentials.json', 'sheets', 'v4', SCOPES)
    
def Export_Data_To_Sheets(dataframe):
    response_date = service.spreadsheets().values().update(
        spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
        valueInputOption='RAW',
        range=SAMPLE_RANGE_NAME,
        body=dict(
            majorDimension='ROWS',
            values=dataframe.T.reset_index().T.values.tolist())
    ).execute()
    print('Sheet successfully Updated')

if __name__=='__main__':
    jira = connect_to_jira(jiraOptions, jira_email, jira_auth_key)
    issue = jira.issue(id='TK-8')
    summary = issue.fields.description.replace('\n', ' ') + '%'
    summaryDictionary = templateVariableSeparator(emailOutput=summary)
    # print(summaryDictionary)
    api_call()
    # # use this to read the values from the sheet
    print(values_input[1:][0])
    oldSummary = {}
    for i in range(len(values_input[1:][0])):
        oldSummary[values_input[0][i]] = values_input[1:][0][i]

    df=pd.DataFrame(oldSummary, index=[0])
    print(df)
    df2=pd.DataFrame(summaryDictionary, index=[0])
    df2["FIRST NAME"] = ' '
    df2["LAST NAME"] = ' '
    df3=pd.concat([df, df2], ignore_index=True, sort=False)
    Export_Data_To_Sheets(df3)
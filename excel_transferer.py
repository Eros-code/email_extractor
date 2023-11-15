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
import os
from google.oauth2 import service_account

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'credentials_new.json'

credentials = None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)


SAMPLE_RANGE_NAME = 'A1:AA1000'

def api_call(creds):
    global values_input, service

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        print({'Response': 'successfully connected to spreadsheet'})
        return sheet
    except:
        print({'Response': 'could not connect to spreadsheet'})

def read_sheet(sheet):
    result_input = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME).execute()
    values_input = result_input.get('values', [])
    print(values_input[1:])

    if not values_input and not values_expansion:
        print('No data found.')

def append_rows_sheet(sheet, input_data):
    result_input = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
                                range=SAMPLE_RANGE_NAME,
                                valueInputOption="USER_ENTERED",
                                insertDataOption="INSERT_ROWS",
                                body={"values":input_data}).execute()
    # values_input = result_input.get('values', [])
    # print(values_input[1:])

    # if not values_input and not values_expansion:
    #     print('No data found.')
    
# def Export_Data_To_Sheets(dataframe):
#     response_date = service.spreadsheets().values().update(
#         spreadsheetId=SAMPLE_SPREADSHEET_ID_input,
#         valueInputOption='RAW',
#         range=SAMPLE_RANGE_NAME,
#         body=dict(
#             majorDimension='ROWS',
#             values=dataframe.T.reset_index().T.values.tolist())
#     ).execute()
#     print('Sheet successfully Updated')

if __name__=='__main__':
    jira = connect_to_jira(jiraOptions, jira_email, jira_auth_key)
    issue = jira.issue(id='TK-8')
    summary = issue.fields.description.replace('\n', ' ') + '%'
    summaryDictionary = templateVariableSeparator(emailOutput=summary)
    # print(summaryDictionary)
    permissions_sheet = api_call(credentials)
    # # use this to read the values from the sheet
    # read_sheet(permissions_sheet)

    # initializing dictionary to be added 
    add_item = {"FIRST NAME" : ''}
    add_item2 = {"LAST NAME" : ''}

    K = 'ACTION'
    
    # using dictionary comprehension 
    res = dict()
    for key in summaryDictionary:
        res[key] = summaryDictionary[key]
        
        # modify after adding K key
        if key == K:
            res.update(add_item)
            res.update(add_item2)

    values_array = [list(res.values())]

    append_rows_sheet(permissions_sheet, values_array)

    # oldSummary = {}
    # for i in range(len(values_input[1:][0])):
    #     oldSummary[values_input[0][i]] = values_input[1:][0][i]

    # df=pd.DataFrame(oldSummary, index=[0])
    # print(df)
    # df2=pd.DataFrame(summaryDictionary, index=[0])
    # df2["FIRST NAME"] = ' '
    # df2["LAST NAME"] = ' '
    # df3=pd.concat([df, df2], ignore_index=True, sort=False)
    # Export_Data_To_Sheets(df3)
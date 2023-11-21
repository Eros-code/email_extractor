import io, os, sys, copy, unittest, datetime, dotenv, traceback
import unittest.mock
from main import *

load_dotenv()

username_test = os.getenv('USERNAME_TEST')
password_test = os.getenv('PASSWORD_TEST')
jira_auth_key = os.getenv('JIRA_AUTH_KEY') #Jira api key
jira_email = os.getenv('JIRA_EMAIL') #email used for Jira account
jira_server = os.getenv('JIRA_SERVER') # Jira board URL, looks like ______.atlassian.net
jiraOptions = {'server': jira_server } 
access_token = os.getenv('access_token')

class email_connection(unittest.TestCase):
    imap_server = "outlook.office365.com"

    def test_email_connector(self):

        imap = imaplib.IMAP4_SSL(imap_server)
        _, response = imap.login(username_test, password_test)

        assert response == [b'LOGIN completed.']


class jira_connection(unittest.TestCase):

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_jira_connector(self, mock_stdout):
        
        connect_to_jira(jiraOptions, jira_email, jira_auth_key)   # Call function.
        
        successful_response = "{'Response': 'connected to jira board successfully'}\n"
        self.assertEqual(successful_response, mock_stdout.getvalue())
      

class github_connection(unittest.TestCase):

    def test_github_connector(self):
        result = read_yaml_from_github(access_token)

        self.assertIsNotNone(result)
       



if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False, failfast=False, buffer=True)
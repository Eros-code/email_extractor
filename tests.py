import os, sys, copy, unittest, datetime, dotenv, traceback
from main import *

load_dotenv()

username_test = os.getenv('USERNAME_TEST')
password_test = os.getenv('PASSWORD_TEST')

class email_connection(unittest.TestCase):
    imap_server = "outlook.office365.com"

    def test_email_connector(self):
        # create an IMAP4 class with SSL 
        imap = imaplib.IMAP4_SSL(imap_server)
        _, response = imap.login(username_test, password_test)
        assert response == [b'LOGIN completed.']



if __name__ == "__main__":
    unittest.main(verbosity=2, exit=False, failfast=True, buffer=True)
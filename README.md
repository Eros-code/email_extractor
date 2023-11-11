# email_extractor

This repo has been made to learn how to extract and read emails from an outlook inbox.

currently to load in your username and password you must make a .env file with the example parameters:

USERNAME=youroutlookusername@outlook.com
PASSWORD=yourpassword

if you run the script and it does not work you will need to do:

python -m pip install python-dotenv

the inbuilt imap lib is used to connect to the office 365 server.

in the main function the line: status, messages = imap.select("imap_test") is used to select the 'imap_test' folder within your emails but this can be changed to any folder you wish including normal 'inbox'.

if you would like to test this yourself using an imap_test folder - it must be created within the outlook client under 'create new folder' you can also set up rules by going to the settings in outlook > rules > add new rule:
add condition emails from (choose an email of your choice)
add action move to imap_test

Following this any emails that are received from the specified email address will be redirected to the imap_test folder.

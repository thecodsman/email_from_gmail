import imaplib
import time
import email
import re
import unittest
import argparse
from datetime import datetime
from unittest import TestCase
from unittest import mock
from collections import Counter
if __name__ == "__main__":
    from email_config import user, password

re.MULTILINE
# --------------------------------------------------------------------------------------------------------------------------------

def define_arguments():
    # define the arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--email', type=str, help='The email to login to (by default is set by email_config.py)')
    parser.add_argument('--password', type=str, help='your password to login to your email (by default set by email_config.py)')
    parser.add_argument('--user-filter', type=str, help='Recipient email address')
    parser.add_argument('--start-date', type=str, help='Start date')
    parser.add_argument('--end-date', type=str, help='End date')
    args = parser.parse_args()
    return args

# --------------------------------------------------------------------------------------------------------------------------------
def get_filters(userFilter, startDate, endDate):
    filters = dict()
    

    if userFilter != '':
        filters['UserFilter'] = userFilter
    else:
        filters['UserFilter'] = 0

    # ask if user wants to use date range
    if startDate is not None: 
        # convert the format from dd/mm/yyyy to d/mmm/yyyy
        startDate = startDate.strftime("%e-%b-%Y").strip() # get rid of whitespace
        endDate = endDate.strftime("%e-%b-%Y").strip()

        filters['StartDate'] = startDate
        filters['EndDate'] = endDate
    else:
        filters['StartDate'] = 0
        filters['EndDate'] = 0
        
    return filters

# -------------------------------------------------------------------------------------------------------------------------------

def select_correct_mail(imap, mailbox, userFilter, startDate, endDate):
    imap.select(mailbox)
    searchFilter = '('
    if userFilter != 0:
        searchFilter += f'TO "{userFilter}"' # if the user is using a filter then it adds it to the filters

    if startDate != 0:
        searchFilter += f'SENTSINCE "{startDate}" SENTBEFORE "{endDate}"'

    searchFilter += ')'

    if searchFilter == '()': # if there are no filters then select all mail
        searchFilter = '(All)'

    status, messages = imap.search(None, searchFilter)
    return messages
        
# -------------------------------------------------------------------------------------------------------------------------------

def get_email_content(imap, message):
    status, data = imap.fetch(message, "(RFC822)")
    for response in data:
        if not isinstance(response, tuple): continue
        # convert the email retrieved from gmail (as a string) into an email object that can be parsed easily
        msg = email.message_from_string(response[1].decode('utf-8'))

        # get the subjects and dates
        subject = msg['subject']
        date = msg['date']
        
        # get the body
        body = ''
        for part in msg.walk():
            if part.get_content_type() != "text/plain": continue
            body = part.get_payload(decode=True)

        try:
            body.decode()
        except:
            pass

    return body, subject, date

# -------------------------------------------------------------------------------------------------------------------------------

def get_most_common_words(string):
    # split the string
    words = string.split()
    alphaNumericWords = []

    for word in words: # get rid of non alpha-numeric words
        if word.isalnum() is not True: continue 
        alphaNumericWords.append(word)
        
    # count them up using the Counter library
    wordCounts = Counter(alphaNumericWords)
    # get the top 10 most common words
    top10Words = wordCounts.most_common(10)

    return top10Words


# ------------------------------------------------------------------------------------------------------------------------------
def run(args):
    # connect
    imap = imaplib.IMAP4_SSL("imap.gmail.com")

    # login
    if args.email is None:
        imap.login(user, password)
    else:
        imap.login(args.email, args.password)

    # get filters
    filters = get_filters(args)

    # get all the emails with the right filters and stuff
    messages = select_correct_mail(imap, '"[Gmail]/All Mail"', filters['UserFilter'], filters['StartDate'], filters['EndDate'])

    # get emails
    print('getting your emails...\n')
    allEmail = ''
    subjectsAndDates = dict()
    for message in messages[0].split():
        # get email content
        body, subject, date = get_email_content(imap, message)

        # append email body to allEmail
        allEmail += str(body)
        # add subject and date pair to subjectsAndDates
        subjectsAndDates[subject] = date

    
    # print the subjects and dates they were sent
    for subject, date in subjectsAndDates.items():
        print(f'Subject: {subject}      Date: {date}\n{"-"*50}')
        time.sleep(0.1) # wait a tenth of a second before printing the next subject and date

    # get top 10 words
    top10Words = get_most_common_words(allEmail)

    # print top 10 words
    print('\ntop 10 words:\n')
    wordCountString = ''
    for word, count in top10Words:
        wordCountString += f'{word}: {count}\n'
    return subjectsAndDates, wordCountString

# ===============================================================================================================================

# unit test
class TestEveryThing(TestCase):
    # Test all the functions
    
    # test the select_correct_mail function by passing in a filter
    def test_select_mail_with_filter(self):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(user, password)
        messages = select_correct_mail(imap, '"[Gmail]/All Mail"', 'todd@spicytg.com', 0, 0)
        print("if this one failed it might just be because you have not sent any emails to todd@spicytg.com")
        self.assertTrue(messages)
        imap.close()
        imap.logout()

    # test the select_correct_mail function by passing in no filter
    def test_select_mail_without_filter(self):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(user, password)
        messages = select_correct_mail(imap, '"[Gmail]/All Mail"', 0, 0, 0)
        self.assertTrue(messages)
        imap.close()
        imap.logout()

    # test the get_emails function by passing in a filter
    def test_get_all_email_with_filter(self):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(user, password)
        messages = select_correct_mail(imap, '"[Gmail]/All Mail"', 'todd@spicytg.com', 0, 0)
        self.assertTrue(messages)

        allEmail = ''
        subjectsAndDates = dict()
        for message in messages[0].split():
            body, subject, date = get_email_content(imap, message)
            allEmail += str(body)
            subjectsAndDates[subject] = date
        imap.close()
        imap.logout()

        self.assertTrue(allEmail)
        self.assertTrue(subjectsAndDates)

    def test_get_all_email_with_date_range(self):
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        imap.login(user, password)
        messages = select_correct_mail(imap, '"[Gmail]/All Mail"', 0, '1-Oct-2022', '15-Dec-2022')
        self.assertTrue(messages)

        allEmail = ''
        subjectsAndDates = dict()
        for message in messages[0].split():
            body, subject, date = get_email_content(imap, message)
            allEmail += str(body)
            subjectsAndDates[subject] = date
        imap.close()
        imap.logout()

        self.assertTrue(allEmail)
        self.assertTrue(subjectsAndDates)

# final stretch

# get arguments

if __name__ == "__main__":
    args = define_arguments()
    useUnitTest = False
    if useUnitTest is True:
        unittest.main()
    else:
        run(args)
    

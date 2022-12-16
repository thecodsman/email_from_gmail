import imaplib
import time
import email
import re
import unittest
from unittest import TestCase
from unittest import mock
from collections import Counter
from email_config import user, password

re.MULTILINE
# --------------------------------------------------------------------------------------------------------------------------------

def ask_user_for_filters():
    filters = dict()
    
    # ask if user wants to filter by recipient
    filterRecipient = input('filter by Recipient? (yes/no): ')
    if filterRecipient.lower() == 'yes':
        filterRecipient = True
        userFilter = input('enter recipient\'s email address: ')

        filters['UserFilter'] = userFilter
    else:
        filterRecipient = False

        filters['UserFilter'] = 0

    # ask if user wants to use date range
    useDateRange = input('use date range? (yes/no): ')
    if useDateRange.lower() == 'yes': 
        useDateRange = True
        startDate = input('Enter start date: ')
        endDate = input('Enter end date: ')

        filters['StartDate'] = startDate
        filters['EndDate'] = endDate
    else:
        useDateRange = False

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

# ===============================================================================================================================

# unit test
class TestEveryThing(TestCase):
    # Test all the functions
    
    # test the ask_user_for_filters function by passing in some filters
    @mock.patch('builtins.input')
    def test_filter_by_recipient(self, mocked_input):
        mocked_input.side_effect = ['yes', 'test@example.com', 'yes', '1-Jan-2022', '31-Dec-2022']
        filters = ask_user_for_filters()
        self.assertTrue(filters['UserFilter'])
        self.assertEqual(filters['UserFilter'], 'test@example.com')
        self.assertTrue(filters['StartDate'])
        self.assertTrue(filters['EndDate'])
        self.assertEqual(filters['StartDate'], '1-Jan-2022')
        self.assertEqual(filters['EndDate'], '31-Dec-2022')

    # test the ask_user_for_filters function by passing in no filters
    @mock.patch('builtins.input')
    def test_no_filter_by_recipient(self, mocked_input):
        mocked_input.side_effect = ['no', 'no']
        filters = ask_user_for_filters()
        self.assertFalse(filters['UserFilter'])
        self.assertEqual(filters['UserFilter'], 0)
        self.assertFalse(filters['StartDate'])
        self.assertFalse(filters['EndDate'])
        self.assertEqual(filters['StartDate'], 0)
        self.assertEqual(filters['EndDate'], 0)
    
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
if __name__ == "__main__":
    useUnitTest = input("Use unit test? (yes/no): ")
    if useUnitTest.lower() == 'yes':
        unittest.main()
    else:
        # connect
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        # login
        imap.login(user, password)

        # get all the emails with the right filters and stuff
        print('The date format is D-MMM-YYYY (eg. 5-Sep-2022 or 12-Aug-2022)')
        filters = ask_user_for_filters()
        messages = select_correct_mail(imap, '"[Gmail]/All Mail"', filters['UserFilter'], filters['StartDate'], filters['EndDate'])

        # get emails
        print('getting your emails...\n')
        allEmail = ''
        subjectsAndDates = dict()
        for message in messages[0].split():
            # get email content
            body, subject, date = get_email_content(imap, messages)

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
        for word, count in top10Words:
            print(f'{word}: {count}')


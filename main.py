import imaplib
import time
import email
import re
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
        print('The date format is D-MMM-YYYY (eg. 5-Sep-2022 or 12-Aug-2022)')
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
        searchFilter = searchFilter + f'TO "{userFilter}"' # if the user is using a filter then it adds it to the filters

    if startDate != 0:
        searchFilter = searchFilter + f'SENTSINCE "{startDate}" SENTBEFORE "{endDate}"'

    searchFilter = searchFilter + ')'

    if searchFilter == '()': # if there are no filters then select all mail
        searchFilter = '(All)'

    status, messages = imap.search(None, searchFilter)
    return messages
        
# -------------------------------------------------------------------------------------------------------------------------------    

def get_email_body(msg):
    body = ''
    for part in msg.walk():
        if part.get_content_type() != "text/plain": continue
        try:
            body = part.get_payload(decode=True).decode()
        except:
            body = part.get_payload(decode=True)

    return body

# -------------------------------------------------------------------------------------------------------------------------------
def get_emails(imap, messages):
    allEmail = ''
    subjectsAndDates = dict()

    # iterate over the messages
    for message in messages[0].split():
        status, data = imap.fetch(message, "(RFC822)")
        for response in data:
            if not isinstance(response, tuple): continue
            msg = email.message_from_string(response[1].decode('utf-8')) # convert the email retrieved from gmail (as a string) into an email object that can be parsed easily

            subject = msg['subject']
            date = msg['date']
            subjectsAndDates[subject] = date # the key is the subject the value is the date
            
            body = get_email_body(msg)
            allEmail += str(body)
                
    
    # close the connection
    imap.close()
    imap.logout()
    return allEmail, subjectsAndDates

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
# final stretch
if __name__ == "__main__":
    # connect
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # login
    imap.login(user, password)

    # get all the emails with the right filters and stuff
    filters = ask_user_for_filters()
    messages = select_correct_mail(imap, '"[Gmail]/All Mail"', filters['UserFilter'], filters['StartDate'], filters['EndDate'])

    print('getting your emails...\n')
    allEmail, subjectsAndDates = get_emails(imap, messages)
    
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


from . import main
import imaplib
import email
from collections import Counter

def THE_function(email, password, userFilter, startDate, endDate):
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    imap.login(email, password)

    subjectsAndDates = {}
    allEmail = ''
    filters = main.get_filters(userFilter, startDate, endDate)
    messages = main.select_correct_mail(imap, '"[Gmail]/All Mail"', filters['UserFilter'], filters['StartDate'], filters['EndDate'])
    for message in messages[0].split():
        body, subject, date = main.get_email_content(imap, message)
        subjectsAndDates[subject] = date
        allEmail += str(body)

    for subject, date in subjectsAndDates.items():
        print(f'Subject: {subject}      ||      Date: {date}')

    words = allEmail.split()
    alnumWords = []
    for word in words:
        if not word.isalnum(): continue
        alnumWords.append(word)

    wordcounts = Counter(alnumWords)
    top10Words = wordcounts.most_common(10)

    for word, count in top10Words:
        print(f'{word}: {count}')

    imap.close()
    imap.logout()
    
    return subjectsAndDates, top10Words

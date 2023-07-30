from celery import shared_task
import time
from web.models import Question
from django.core.mail import send_mail

@shared_task
def test_func(url,method):
    time.sleep(5)
    print("REQUEST", method, 'on', url)

@shared_task
def send_email(question: Question):
    email = question.author.email
    url = f'http://hasker.ru/ask{question.pk}'
    subject="new reply"
    recipient_list = [email]
    message = f'Your question got new reply\n{url}'
    from_email = 'notify@hasker.ru'
    # send_mail(subject, message, from_email, recipient_list)
    print("#### NEW EMAIL ####")
    print('from',from_email, 'to',recipient_list)
    print("subject", subject)
    print(message)
    print("#### END ####")
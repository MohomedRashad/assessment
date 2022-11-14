from django.conf import settings
from random import randint
from datetime import datetime

from apps.common.tasks import send_email


def generate_token(token_length):
    range_start = 10 ** (token_length - 1)
    range_end = (10 ** token_length) - 1
    return randint(range_start, range_end)


def send_mail(subject, to, template=None, data=None, message=None):
    if settings.ENABLE_CELERY:
        send_email.delay(subject, to, template, data, message)
    else:
        send_email(subject, to, template, data, message)

def is_the_appointment_slot_exactly_15_minutes(time1, time2):
    start_time = datetime.strptime(time1.isoformat(), "%H:%M:%S")
    end_time = datetime.strptime(time2.isoformat(), "%H:%M:%S")
    delta = end_time - start_time
    sec = delta.total_seconds()
    min = sec / 60
    if min == 15:
        return True
    else:
        return False

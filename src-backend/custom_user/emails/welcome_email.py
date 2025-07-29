import os
from django.conf import settings
from django.apps import apps
from health_competition.celery import app

from .multipurpose import send_email


@app.task()
def welcome_email(user_pk):
    """Welcome with email verification and payment instructions"""
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_obj = CustomUser.objects.get(pk=user_pk)

    email_subject = 'Welcome to the Health Competition!'

    with open(os.path.join("custom_user", "emails", "templates", "welcome.html"), "r") as file:
        email_body = file.read()

    first_name = user_obj.first_name

    if user_obj.strava_refresh_token is None or user_obj.strava_refresh_token == '':
        with open(os.path.join("custom_user", "emails", "templates", "link_strava.html"), "r") as file:
            strava_block = file.read()
    else:
        strava_block = ""

    email_body = email_body.format(first_name=first_name, LINK_STRAVA_BLOCK=strava_block)

    send_email(subject=email_subject, body=email_body, to_email=user_obj.email)

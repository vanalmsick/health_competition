import os
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives



def send_email(subject, body, to_email, cc=[], reply_to=[]):
    """General function via which all emails are sent out"""
    to_email = [settings.EMAIL_FROM] if (settings.DEBUG or '.local' in to_email.lower()) else [to_email]
    from_email = settings.EMAIL_FROM
    reply_to_email = [from_email] if settings.EMAIL_REPLY_TO is None else settings.EMAIL_REPLY_TO
    with open(os.path.join("custom_user", "emails", "templates", "base.html"), "r") as file:
        email_template = file.read()

    html_message = email_template
    for tag, replace_value in dict(
            MAIN_BODY=body, EMAIL_SUBJECT=subject, EMAIL_REPLY_TO=reply_to_email[0], MAIN_HOST=settings.MAIN_HOST
    ).items():
        html_message = html_message.replace("{" + f"{tag}" + "}", str(replace_value))

    print(f'Email Server: {settings.EMAIL_HOST}')
    connection = get_connection()
    mail = EmailMultiAlternatives(
        subject=subject, body="", from_email=from_email, to=to_email, cc=cc, reply_to=reply_to,
        connection=connection
    )
    mail.attach_alternative(html_message, "text/html")
    mail.content_subtype = "html"

    mail.send()
    print(f'Email "{subject}" sent to {to_email}')

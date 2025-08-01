import datetime
from django.conf import settings
from django.apps import apps
from django.template.loader import render_to_string
from health_competition.celery import app
from django.db.models import Q

from .multipurpose import send_email
from competition.stats import get_competition_stats


@app.task()
def welcome_email(user_pk):
    """Welcome email for new users."""
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_obj = CustomUser.objects.get(pk=user_pk)

    email_subject = 'Welcome to the Health Competition!'

    if user_obj.strava_refresh_token is None or user_obj.strava_refresh_token == '':
        strava_block = render_to_string(
            "email_link_strava.html",
            {
                'MAIN_HOST': settings.MAIN_HOST,
            }
        )
    else:
        strava_block = ""

    email_body = render_to_string(
        "email_welcome.html",
        {
            'first_name': user_obj.first_name,
            'MAIN_HOST': settings.MAIN_HOST,
            'LINK_STRAVA_BLOCK': strava_block,
            'EMAIL_REPLY_TO': settings.EMAIL_REPLY_TO,
        }
    )

    if settings.DEBUG:
        with open('tmp_email.html', 'w') as file:
            file.write(email_body)

    send_email(subject=email_subject, body=email_body, to_email=user_obj.email)

    return {'pk': user_obj.pk, 'username': user_obj.username, 'email': user_obj.email}


@app.task()
def send_all_log_workouts_email():
    print("Scheduling log workout emails...")
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_lst = CustomUser.objects.filter(
        Q(my_competitions__start_date__lte=datetime.date.today()) &
        Q(my_competitions__end_date__gte=datetime.date.today()) &
        (Q(strava_refresh_token__isnull=True) | Q(strava_refresh_token=''))
    ).order_by('pk')
    task_log = []
    if len(user_lst) > 0:
        eta_steps = max(min((60 * 60) // len(user_lst), 60), 10)
        eta = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10)
        for user_obj in user_lst:
            result = log_workouts_email.apply_async(args=[user_obj.pk], eta=eta)
            task_log.append({'pk': user_obj.pk, 'username': user_obj.username, 'email': user_obj.email, 'task_id': result.task_id, 'eta': eta.isoformat()})
            eta += datetime.timedelta(seconds=eta_steps)
    return task_log


@app.task()
def log_workouts_email(user_pk):
    """Email reminder for users to please log their workouts."""
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_obj = CustomUser.objects.get(pk=user_pk)
    workout_obj_lst = user_obj.workout_set.order_by('-start_datetime')[:3]

    email_subject = 'Health Competition - Log Your Workouts!'

    if user_obj.strava_refresh_token is None or user_obj.strava_refresh_token == '':
        strava_block = render_to_string(
            "email_link_strava.html",
            {
                'MAIN_HOST': settings.MAIN_HOST,
            }
        )
    else:
        strava_block = ""

    email_body = render_to_string(
        "email_log_workouts.html",
        {
            'first_name': user_obj.first_name,
            'last_workouts': workout_obj_lst,
            'MAIN_HOST': settings.MAIN_HOST,
            'LINK_STRAVA_BLOCK': strava_block,
            'EMAIL_REPLY_TO': settings.EMAIL_REPLY_TO,
        }
    )

    if settings.DEBUG:
        with open('tmp_email.html', 'w') as file:
            file.write(email_body)

    send_email(subject=email_subject, body=email_body, to_email=user_obj.email)

    return {'pk': user_obj.pk, 'username': user_obj.username, 'email': user_obj.email}


@app.task()
def send_all_leaderboard_emails():
    print("Scheduling leaderboard emails...")
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_lst = CustomUser.objects.filter(my_competitions__start_date__lt=datetime.date.today(), my_competitions__end_date__gte=datetime.date.today()).order_by('pk')
    eta_steps = max(min((60 * 60) // len(user_lst), 60), 10)
    eta = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=10)
    task_log = []
    for user_obj in user_lst:
        result = leaderboard_email.apply_async(args=[user_obj.pk], eta=eta)
        task_log.append({'pk': user_obj.pk, 'username': user_obj.username, 'email': user_obj.email, 'task_id': result.task_id, 'eta': eta.isoformat()})
        eta += datetime.timedelta(seconds=eta_steps)
    return task_log


@app.task()
def leaderboard_email(user_pk):
    """Email to send users their leaderboard."""
    CustomUser = apps.get_model('custom_user', 'CustomUser')
    user_obj = CustomUser.objects.get(pk=user_pk)

    competition_data = []

    for competition in user_obj.my_competitions.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today()).order_by('-start_date'):
        competition_stats = get_competition_stats(competition.pk)
        competition_data.append({
            'competition': competition_stats['competition'],
            'leaderboard': competition_stats['leaderboard'],
        })

    email_subject = 'Health Competition - Your Spot on the Leaderboard!'

    email_body = render_to_string(
        "email_leaderboard.html",
        {
            'first_name': user_obj.first_name,
            'MAIN_HOST': settings.MAIN_HOST,
            'competitions': competition_data,
            'EMAIL_REPLY_TO': settings.EMAIL_REPLY_TO,
        }
    )

    if settings.DEBUG:
        with open('tmp_email.html', 'w') as file:
            file.write(email_body)

    send_email(subject=email_subject, body=email_body, to_email=user_obj.email)

    return {'pk': user_obj.pk, 'username': user_obj.username, 'email': user_obj.email}

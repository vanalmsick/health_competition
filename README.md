# Workout Challenge
Compete with friends and co-workers across devices (Apple / Android / Garmin / etc.) using the metrics you want to use (km / minutes / kcal / # of times / etc.) respecting your privacy.

## How does it work?
Create a competition, invite friends, and enter workouts manually or link your Strava for automatic workout import.

**Your Personal Dashboard:**
![Preview Dashboard](/docs/imgs/preview-dashboard.png)

**Competition Dashboards:**
![Preview Competition](/docs/imgs/preview-competition.png)

## Quick Start
```
docker run vanalmsi/health_competition -p 80:80
```

## Full Production Deployment
[**docker-compose.yml**](/docker-compose.yml)
```
version: '3.9'

services:
  healthcompetition:
    image: vanalmsick/health_competition
    container_name: healthcompetition
    ports:
      - "80:80"
      - "5555:5555" # Celery Flower task monitoring - do not open to public - only for local network for debugging
      - "9001:9001" # Supervisord process monitoring - do not open to public - only for local network for debugging
      - "8000:8000" # Django admin space - do not open to public - only for local network for debugging
    volumes:
      - /usr/pi/health_competition/django:/health_competition/src-backend/data
    environment:
      - POSTGRES_HOST=healthcompetition-database
      - POSTGRES_DB=healthcompetition
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
      - MAIN_HOST=http://your-url.com
      - HOSTS=http://your-url.com,http://localhost,http://127.0.0.1
      - SECRET_KEY=<your_random_string_for_encryption>
      - TIME_ZONE=Europe/London
      - STRAVA_CLIENT_ID=000000
      - STRAVA_CLIENT_SECRET=<secret_key>
      - REACT_APP_SENTRY_DSN=https://<PUBLIC_KEY>@<HOST>/<PROJECT_ID>
      - EMAIL_HOST=smtp.gmail.com
      - EMAIL_PORT=465
      - EMAIL_HOST_USER=competition@yourdomain.com
      - EMAIL_HOST_PASSWORD=password
      - EMAIL_USE_SSL=True
      - EMAIL_USE_TLS=False
      - EMAIL_FROM=competition@yourdomain.com
      - EMAIL_REPLY_TO=support@yourdomain.com
    restart: unless-stopped
    depends_on:
      database:
        condition: service_healthy

  database:
    image: postgres:15
    container_name: healthcompetition-database
    environment:
      - POSTGRES_DB=healthcompetition
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - /usr/pi/health_competition/postgres:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: [ "CMD-SHELL", "pg_isready -U postgres" ]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Environment variables
| Variable              | Default                             | Definition                                                                                                                                                                                                                                                                                                      |
|-----------------------|-------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MAIN_HOST             | "http://localhost"                  | The main hosting url for the Django backend.                                                                                                                                                                                                                                                                    |
| HOSTS                 | "http://localhost,http://127.0.0.1" | Comma seperated list of hosts for Django. This is used for [ALLOWED_HOSTS](https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts), [CORS_ALLOWED_ORIGINS](https://pypi.org/project/django-cors-headers/), and [CSRF_TRUSTED_ORIGINS](https://pypi.org/project/django-cors-headers/).                |
| SECRET_KEY            | [a hard-coded string in code]       | Django's [SECRET_KEY](https://docs.djangoproject.com/en/5.2/ref/settings/#std-setting-SECRET_KEY) for cryptographic signing.                                                                                                                                                                                    |
| TIME_ZONE             | "Europe/London"                     | Timezone for [Django](https://docs.djangoproject.com/en/5.2/ref/settings/#time-zone) and [Celery](https://docs.celeryq.dev/en/stable/userguide/configuration.html#timezone)                                                                                                                                     |
| DEBUG                 | false                               | Django's DEBUG mode. If true, [CORS_ALLOW_ALL_ORIGINS](https://pypi.org/project/django-cors-headers/) will also be true and the [CACHE](https://docs.djangoproject.com/en/5.2/ref/settings/#caches) will use [Local Memory Cache](https://docs.djangoproject.com/en/5.2/ref/settings/#caches) instead of Redis. |
| POSTGRES_HOST         | None                                | If set to None, Django will use SQLite as database (might cause database lock errors in production), else this is the host url to the [Postgres database](https://hub.docker.com/_/postgres/).                                                                                                                  |
| POSTGRES_DB           | "postgres"                          | Database name in [Postgres database](https://hub.docker.com/_/postgres/)                                                                                                                                                                                                                                        | 
| POSTGRES_USER         | "postgres"                          | Database username in [Postgres database](https://hub.docker.com/_/postgres/)                                                                                                                                                                                                                                    | 
| POSTGRES_PASSWORD     | ""                                  | Database password in [Postgres database](https://hub.docker.com/_/postgres/)                                                                                                                                                                                                                                    | 
| REACT_APP_SENTRY_DSN  | None                                | If None no [Sentry.io](https://sentry.io/) error capturing, else please provide the project url https://<PUBLIC_KEY>@<HOST>/<PROJECT_ID>                                                                                                                                                                        | 
| STRAVA_CLIENT_ID      | "1234321"                           | [Strava API](https://developers.strava.com) Client Id. Please see below how to get one.                                                                                                                                                                                                                         | 
| STRAVA_CLIENT_SECRET  | "ReplaceWithClientSecret"           | [Strava API](https://developers.strava.com) Client Secret. Please see below how to get one.                                                                                                                                                                                                                     | 
| STRAVA_LIMIT_15MIN    | 100                                 | [Strava API](https://developers.strava.com) Limit per 15min. 300 if part of developer program, else 100.                                                                                                                                                                                                        | 
| STRAVA_LIMIT_DAY      | 1000                                | [Strava API](https://developers.strava.com) Limit per day. 3000 if part of developer program, else 1000.                                                                                                                                                                                                        | 
| REACT_APP_BACKEND_URL | ""                                  | Overwrite the url to the Django API used by React. This is intended for local development outside of the docker container - e.g. http://localhost:8000.                                                                                                                                                         | 
| EMAIL_HOST            | None                                | SMTP server host url to send out automated emails.                                                                                                                                                                                                                                                              | 
| EMAIL_PORT            | None                                | SMTP server port to send out automated emails.                                                                                                                                                                                                                                                                  | 
| EMAIL_HOST_USER       | None                                | SMTP server username to send out automated emails.                                                                                                                                                                                                                                                              | 
| EMAIL_HOST_PASSWORD   | None                                | SMTP server password to send out automated emails.                                                                                                                                                                                                                                                              | 
| EMAIL_USE_SSL         | False                               | SMTP server - if SSL ise used for authentication.                                                                                                                                                                                                                                                               | 
| EMAIL_USE_TLS         | False                               | SMTP server - if TLS ise used for authentication.                                                                                                                                                                                                                                                               | 
| EMAIL_FROM            | None                                | Sender email address of automated emails.                                                                                                                                                                                                                                                                       | 
| EMAIL_REPLY_TO        | None                                | Reply-To email address of automated emails.                                                                                                                                                                                                                                                                     | 

### How to get the Strava API Client id & secret
1. Login to your Strava account [strava.com/login](https://www.strava.com/login)
2. Profile picture -> Settings
3. "My API Application"
4. Test the competition (only works with your own Strava account)
5. If you like the competition, apply to the [Strava developer program](https://share.hsforms.com/1VXSwPUYqSH6IxK0y51FjHwcnkd8) here to also allow other users to link their Strava

## Do you want to help / contribute?
### Code Overview / Structure
- [**Docker Container**](/Dockerfile) for deployment 
- [**Supervisord**](supervisord.conf) to start all processes in docker container
- [**Nginx**](/nginx.conf) to run frontend (React) and proxy traffic to backend (Django) which is run by gunicorn
#### Frontend *([src-frontend](/src-frontend))*
- [**React**](/src-frontend/src/App.js)
#### Backend *([src-backend](/src-backend))*
- [**Django**](/src-backend/health_competition/settings.py) (RestAPI) via gunicorn for production
- [**Redis**](supervisord.conf) as cache/memory and for Celery
- [**Celery**](/src-backend/health_competition/celery.py) as task que for Django
- [**Celery Beat**](supervisord.conf) for task scheduling for Django
- [**Celery Flower**](supervisord.conf) UI to inspect task que and task status

### How to run it in dev
#### Backend - Task-Scheduling (Celery)
**working dir:** `/health_competition/src-backend`  
**executable for Redis:** `redis-server`  
**executable for Celery Worker:** `celery -A health_competition worker --loglevel INFO --without-mingle --without-gossip`  
**executable for Celery Beat:** `celery -A health_competition beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel INFO`  
**executable for Celery Flower:** `celery -A health_competition flower`  

#### Backend - RESTApi Server (Django)
**working dir:** `/health_competition/src-backend`  
**additional env variables:**
```
PYTHONUNBUFFERED=1
DJANGO_SETTINGS_MODULE=health_competition.settings
DEBUG=true
MAIN_HOST=http://localhost
HOSTS=http://localhost,http://127.0.0.1
TIME_ZONE=Europe/London
STRAVA_CLIENT_ID=000000
STRAVA_CLIENT_SECRET=<secret_key>
```
**executable for Django Setup:** `python manage.py makemigrations && python manage.py migrate`  
**executable for Django:** `python manage.py runserver`  
#### Frontend (React)
**working dir:** `/health_competition/src-frontend`  
**env variables:**
```
REACT_APP_BACKEND_URL=http://localhost:8000
```
**executable:** `npm start`

### ToDos:
- Improve modal to change teams (plus access right issue if not owner)
- User account deletion causes "maximum recursion depth exceeded" error
- Competition start & finish email

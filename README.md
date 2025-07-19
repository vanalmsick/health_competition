# Health Competition
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
**docker-compose.yml**
```
version: '3.9'

services:
  healthcompetition:
    container_name: healthcompetition
    build: .
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

### Steps to get the Strava API Client id & secret
1. Login to your Strava account [strava.com/login](https://www.strava.com/login)
2. Profile picture -> Settings
3. "My API Application"

## Do you want to help / contribute?
### Code Overview / Structure
- **Docker Container** for deployment 
- **Supervisord** to start all processes in docker container
- **Nginx** to run frontend (React) and proxy traffic to backend (Django) which is run by gunicorn
#### Frontend *(src-frontend)*
- **React**
#### Backend *(src-backend)*
- **Django** (RestAPI) via gunicorn for production
- **Redis** as cache/memory and for Celery
- **Celery** as task que for Django
- **Celery Beat** for task scheduling for Django
- **Celery Flower** UI to inspect task que and task status

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
- Fix calendar if 30 days cause 6 weeks
- Improve modal to change teams
- Add password reset functionality

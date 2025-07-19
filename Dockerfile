FROM node:18 AS frontend
WORKDIR /health_competition/src-frontend
COPY src-frontend/ /health_competition/src-frontend/
RUN npm install && npm run build

FROM python:3.11-alpine AS backend
WORKDIR /health_competition/src-backend
COPY src-backend/ /health_competition/src-backend/

# Install build dependencies for psycopg2
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev
RUN pip install --no-cache-dir -r requirements.txt

# Collect Django static files
RUN python3 manage.py collectstatic --noinput

FROM python:3.11-alpine AS final

# Install system dependencies
RUN apk add --no-cache nginx supervisor build-base redis postgresql-libs

# Install build dependencies for psycopg2
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev nano

# Set workdir
WORKDIR /health_competition

# Copy backend code
COPY --from=backend /health_competition/src-backend /health_competition/src-backend

# Copy requirements and install them again
COPY src-backend/requirements.txt /health_competition/src-backend/requirements.txt
RUN pip install --no-cache-dir -r /health_competition/src-backend/requirements.txt && pip install gunicorn

# Copy frontend build
COPY --from=frontend /health_competition/src-frontend/build /usr/share/nginx/html

# Copy configs
COPY nginx.conf /etc/nginx/http.d/default.conf
COPY supervisord.conf /etc/supervisord.conf

# NGINX runtime folder
RUN mkdir -p /run/nginx

# Django data folder with mirgations and sqlite database
VOLUME /health_competition/src-backend/data

# the app
EXPOSE 80
# supervisord - monitoring of running apps
EXPOSE 9001
# celery flower - monitoring of celery tasks
EXPOSE 5555

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
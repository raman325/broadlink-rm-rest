# Broadlink-RM-REST: A REST server to interact with local Broadlink RM IR/RF blasters
# 
#

FROM python:2.7.15-slim-stretch

# create volume for SQLite DB files
VOLUME ["app/data"]

# install dependencies
RUN pip install falcon peewee broadlink gunicorn psycopg2-binary

# environment vaariables
ENV HOST "0.0.0.0"
ENV PORT "8000"
ENV BROADLINK_STATUS_TIMEOUT "1"
ENV BROADLINK_DISCOVERY_TIMEOUT "5"

# ENV GUNICORN_CMD_ARGS="--bind=${HOST}:${PORT}"

# set up app directory
COPY ./app /app
WORKDIR /app

# open $PORT
EXPOSE $PORT

# start application
# ENTRYPOINT exec gunicorn broadlink_rm_rest_app:app
COPY ./docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

# Broadlink-RM-REST: A REST server to interact with local Broadlink RM IR/RF blasters
# 
#

FROM python:2.7.15-alpine3.7

# create volume for SQLite DB files
VOLUME ["/data"]

# install dependencies
RUN pip install falcon peewee broadlink gunicorn psycopg2-binary

ENV HOST "0.0.0.0"
ENV PORT "8000"
ENV GUNICORN_CMD_ARGS="--bind=${HOST}:${PORT}"

# Set up app directory
COPY ./app /app
WORKDIR /app

EXPOSE $PORT

ENTRYPOINT exec gunicorn broadlink_rm_rest_app:app
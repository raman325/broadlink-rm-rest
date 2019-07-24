# Broadlink-RM-REST: A REST server to interact with local Broadlink RM IR/RF blasters
# 
#

FROM python:3-slim

# create volume for SQLite DB files
VOLUME ["app/data"]

# install dependencies
RUN pip3 install falcon peewee gunicorn broadlink==0.10

# environment vaariables
ENV HOST "0.0.0.0"
ENV PORT "8000"
ENV BROADLINK_STATUS_TIMEOUT "1"
ENV BROADLINK_DISCOVERY_TIMEOUT "5"

# set up app directory
COPY ./app /app
WORKDIR /app

# open $PORT
EXPOSE $PORT

# start application
COPY ./docker-entrypoint.sh /app
RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Broadlink-RM-REST: A REST server to interact with local Broadlink RM IR/RF blasters
# 
#

FROM python:3-alpine

# create volume for SQLite DB files
VOLUME ["app/data"]

RUN apk add --no-cache make build-base

# install dependencies
RUN pip3 install falcon peewee gunicorn broadlink==0.10

# remove unneded packages
RUN apk del make build-base
RUN apt-get autoremove autoclean

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
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

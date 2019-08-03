# Broadlink-RM-REST: A REST server to interact with local Broadlink RM IR/RF blasters
# 
#

FROM python:3-alpine

# create volume for SQLite DB files
VOLUME ["app/data"]

ADD requirements.txt /
RUN cd  && ls
# Install dependencies to build packages
RUN apk add --no-cache --virtual .build-deps build-base \
## Install dependencies needed for project
    && pip3 install -r requirements.txt \
    && runDeps="$( \
        scanelf --needed --nobanner --recursive /usr/local \
                | awk '{ gsub(/,/, "\nso:", $2); print "so:" $2 }' \
                | sort -u \
                | xargs -r apk info --installed \
                | sort -u \
    )" \
    && apk add --virtual .rundeps $runDeps \
    && apk del .build-deps

RUN apk del build-base && \
            rm -rf /usr/share/locale/* && \
            rm -rf /var/cache/debconf/*-old && \
            rm -rf /var/lib/apt/lists/* /var/lib/dpkg   && \
            rm -rf /usr/share/doc/* && \
            rm -rf /usr/share/man/?? && \
            rm -rf /usr/share/man/??_*


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

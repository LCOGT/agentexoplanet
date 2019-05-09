FROM python:3.6-alpine

# default working directory
WORKDIR /app

# install depedencies
COPY requirements.txt .
RUN apk --no-cache add libgomp libjpeg-turbo mariadb-connector-c zlib \
        && apk --no-cache add --virtual .build-deps \
                g++ \
                gcc \
                git \
                libjpeg-turbo-dev \
                mariadb-dev \
                musl-dev \
                zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r requirements.txt \
        && apk --no-cache del .build-deps

# install web application
COPY app/ .

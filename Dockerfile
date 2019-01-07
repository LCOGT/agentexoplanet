FROM python:3.6-alpine
MAINTAINER Edward Gomez <egomez@lco.global>

ENTRYPOINT [ "/init" ]


# set the PREFIX env variable
ENV PREFIX /agentexoplanet

# install depedencies
COPY app/requirements.txt /var/www/apps/agentex/requirements.txt
RUN apk --no-cache add dcron libjpeg-turbo mariadb-connector-c nginx supervisor zlib libgomp \
        && apk --no-cache add --virtual .build-deps gcc g++ git \
                libjpeg-turbo-dev mariadb-dev musl-dev zlib-dev \
        && pip --no-cache-dir --trusted-host=buildsba.lco.gtn install -r /var/www/apps/agentex/requirements.txt \
        && apk --no-cache del .build-deps

# install entrypoint
COPY config/ /

# install web application
COPY app /var/www/apps/agentex/

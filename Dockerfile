FROM centos:7
MAINTAINER Edward Gomez <egomez@lcogt.net>

EXPOSE 80
ENTRYPOINT [ "/init" ]

# setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE core.settings

# set the PREFIX env variable
ENV PREFIX /agentexoplanet

# install and update packages
RUN yum -y install epel-release \
        && yum -y install gcc make mysql-devel python-devel python-pip nginx supervisor \
        && yum -y update \
        && yum -y clean all

COPY app/requirements.txt /var/www/apps/agentexoplanet/requirements.txt

# install Python packages
RUN pip install --upgrade pip setuptools \
        && pip install -r /var/www/apps/agentexoplanet/requirements.txt \
        && rm -rf /root/.pip /root/.cache

RUN useradd uwsgi && gpasswd -a uwsgi uwsgi

# copy configuration files
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini
COPY config/init /init

# install webapp
COPY app /var/www/apps/agentexoplanet

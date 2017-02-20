FROM centos:7
MAINTAINER Edward Gomez <egomez@lcogt.net>

EXPOSE 80
ENTRYPOINT [ "/init" ]

# install and update packages
RUN yum -y install epel-release \
        && yum -y install gcc make mysql-devel python-devel python-pip \
                python-matplotlib nginx supervisor \
        && yum -y update \
        && yum -y clean all

COPY app/requirements.txt /var/www/apps/agentexoplanet/requirements.txt

# install Python packages
RUN pip install --upgrade 'pip>=8.1.1' \
        && pip install 'uwsgi==2.0.13.1' \
        && pip install -r /var/www/apps/agentexoplanet/requirements.txt \
        && rm -rf /root/.pip /root/.cache

# setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE core.settings

# set the PREFIX env variable
ENV PREFIX /agentexoplanet

# copy configuration files
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini
COPY config/init /init

# install webapp
COPY app /var/www/apps/agentexoplanet

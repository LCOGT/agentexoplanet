######################################
#
# LCOGT docker build file for CitSci portal
# This contains NGINx and uWSGI components in 1 container
#
# To build
# docker build -t docker.lcogt.net/agentex:latest .
#
# To push to repo
# docker push docker.lcogt.net/agentex:latest
#
# To start docker container
# docker run -d -p 8900:80 --name=agentex  -m="128m" --restart=always -v /net/mfs/data4/agentexoplanet:/var/www/agentexoplanet/media/data docker.lcogt.net/citsciportal:latest
#
######################################

FROM centos:centos7
MAINTAINER Edward Gomez <egomez@lcogt.net>

# install and update packages
RUN yum -y install epel-release \
        && yum -y install gcc make mysql-devel python-devel python-pip python-matplotlib  \
        && yum -y install nginx supervisor \
        && yum -y update \
        && yum -y clean all

COPY app/requirements.txt /var/www/apps/agentexoplanet/requirements.txt

# install Python packages
RUN pip install pip==1.3 && pip install uwsgi==2.0.8 \
		&& pip install -r /var/www/apps/agentexoplanet/requirements.txt

# Setup the Python Django environment
ENV PYTHONPATH /var/www/apps
ENV DJANGO_SETTINGS_MODULE core.settings

# Set the PREFIX env variable
ENV PREFIX /agentexoplanet

# Copy configuration files
COPY config/uwsgi.ini /etc/uwsgi.ini
COPY config/nginx/* /etc/nginx/
COPY config/processes.ini /etc/supervisord.d/processes.ini

# httpd on port 80
EXPOSE 80

# we run under supervisord
ENTRYPOINT [ "/init" ]

# Copy configuration files
COPY config/init /init

# install webapp
COPY app /var/www/apps/agentexoplanet

# Setup the LCOGT agentexoplanet webapp
RUN python /var/www/apps/agentexoplanet/manage.py collectstatic --noinput
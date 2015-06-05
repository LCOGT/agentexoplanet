######################################
#
# LCOGT docker build file for CitSci portal
# This contains NGINx and uWSGI components in 1 container
#
# To build
# docker build -t docker.lcogt.net/citsciportal:latest .
#
# To push to repo
# docker push docker.lcogt.net/citsciportal:latest
#
# To start docker container
# docker run -d -p 8900:80 --name=agentex  -m="128m" --restart=always -v /net/mfs/data4/agentexoplanet:/var/www/agentexoplanet/media/data docker.lcogt.net/citsciportal:latest
#
######################################

FROM centos:centos7
MAINTAINER Ira W. Snyder <isnyder@lcogt.net>

# httpd on port 80
EXPOSE 80

# we run under supervisord
ENTRYPOINT [ "/usr/bin/supervisord", "-n", "-c", "/etc/supervisord.conf" ]

# Setup the Python Django environment
ENV PYTHONPATH /var/www/agentexoplanet
ENV DJANGO_SETTINGS_MODULE agentexoplanet.settings

# install and update packages
RUN yum -y install epel-release \
        && yum -y install gcc make mysql-devel python-devel python-pip \
        && yum -y install numpy python-matplotlib \
        && yum -y install httpd mod_wsgi supervisor \
        && yum -y update \
        && yum -y clean all

# install configuration
COPY docker/processes.ini /etc/supervisord.d/
COPY docker/agentexoplanet.conf /etc/httpd/conf.d/

# install webapp
COPY . /var/www/agentexoplanet

# install Python packages
RUN pip install -r /var/www/agentexoplanet/pip-requirements.txt

# remove extra stuff
RUN rm -rf /var/www/agentexoplanet/docker \
        && rm -f /var/www/agentexoplanet/Dockerfile \
        && rm -f /var/www/agentexoplanet/pip-requirements.txt \
        && rm -f /var/www/agentexoplanet/README.md

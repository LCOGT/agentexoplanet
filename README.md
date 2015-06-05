Citizen Science Portal
======================

This project contains Agent Exoplanet and Show Me Stars.

Agent Exoplanet
---------------

First citizen science project for LCOGT. It involves the analysis of exoplanet transit data. 

Show Me Stars
-------------

Celebrities use RTI to control one of our 2-meter telescopes for 1 hour and tweet their images.

Docker
======

This project has been converted to use Docker as the deployment method.

Instructions
------------

    $ docker build -t registry.lcogt.net/agentexoplanet .
    $ docker run -d -p 8888:80 -m 256m -v /path/to/data:/var/www/agentexoplanet/media/data registry.lcogt.net/agentexoplanet

TODO
----

* Update Django so that we can use nginx + uwsgi as the web server
* Rework the `setting.py` code to match the other projects
* Split apart "Agent Exoplanet" and "Show Me Stars" (maybe?)
* Figure out a more permanent home for the FITS data (~6GB, NFS?)
* Fix broken "Show Me Stars" logo image on index page

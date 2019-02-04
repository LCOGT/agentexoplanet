Citizen Science Portal
======================

This project contains Agent Exoplanet.


Agent Exoplanet
---------------


Adding a new dataset
--------------------

1. Enter the Django-admin and, under ‘Agent Exoplanet Administration’ locate ‘Transit events’ and click to enter.
2. In the top right, select ‘Add new event’.
3. Populate the details (all are required). NOTE: FOR NOW LET THE FINDER ID BE ANY NUMBER NOT ALREADY ASSOCIATED WITH ANOTHER DATASET (1 is a good choice for now).
1. Add `fits` and `jpgs` folders for new event under `DATA_LOCATION/<event_slug>` e.g. `DATA_LOCATION/wasp43b/fits/` 
1. In a Terminal window, run `python manage.py loadplanetdata --event_id <event_slug>` to add all data files
1. Run `python manage.py findsources --event_id <event_slug>` to identify catalogue stars


Docker
======

This project has been converted to use Docker as the deployment method.

Instructions
------------

    $ docker build -t docker.lco.global/agentex:latest .
    $ docker push docker.lco.global/agentex:latest

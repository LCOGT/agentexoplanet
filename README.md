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
4. Repeat 3. for ‘Transit targets’.
5. Run `python manage.py shell` in a terminal window in the root folder of the project. This will open a Python shell.
6. Run `from agentex.models import Event, Target` and then `planet_name = Event.objects.filter(event=‘planet_name’)` where `planet_name` is the name given to the event in 3..
7. Run `planet_name.event`
5. In a Terminal window, run `python manage.py loadplanetdata`.
=======
First citizen science project for LCOGT. It involves the analysis of exoplanet transit data.

Docker
======

This project has been converted to use Docker as the deployment method.

Instructions
------------

    $ docker build -t docker.lcogt.net/agentex:latest .
    $ docker push docker.lcogt.net/agentex:latest

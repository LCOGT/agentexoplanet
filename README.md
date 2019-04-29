# Agent Exoplanet

An educational project produced by the [Las Cumbres Observatory](https://lco.global/).

## Adding a new dataset

1. Enter the Django-admin and, under ‘Agent Exoplanet Administration’ locate ‘Transit events’ and click to enter.
2. In the top right, select ‘Add new event’.
3. Populate the details (all are required). NOTE: FOR NOW LET THE FINDER ID BE ANY NUMBER NOT ALREADY ASSOCIATED WITH ANOTHER DATASET (1 is a good choice for now).
4. Add `fits` and `jpgs` folders for new event under `DATA_LOCATION/<event_slug>` e.g. `DATA_LOCATION/wasp43b/fits/` 
5. In a Terminal window, run `python manage.py loadplanetdata --event_id <event_slug>` to add all data files
6. Run `python manage.py findsources --event_id <event_slug>` to identify catalogue stars

## Build

This project is built automatically by the [LCO Jenkins Server](http://jenkins.lco.gtn/).
Please see the [Jenkinsfile](Jenkinsfile) for further details.

## Production Deployment

This project is deployed to the LCO Kubernetes Cluster. Please see the
[LCO Helm Charts Repository](https://github.com/LCOGT/helm-charts) for further
details.

## License

This project is licensed under the GNU GPL v3. Please see the [LICENSE](LICENSE)
file for further details.

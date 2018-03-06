.. highlight:: shell

===============================
Overscaler
===============================

.. image:: https://circleci.com/gh/GleamAI/overscaler.svg?style=shield&circle-token=0a5ec2f06068e12bd8924db36ac00c24a8eee40a
    :target: https://circleci.com/gh/GleamAI/overscaler

.. image:: https://readthedocs.org/projects/overscaler/badge/?version=latest
	:target: http://overscaler.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status
                

Stateful sets autoscaler for Google Kubernetes Engine.

* Documentation: https://overscaler.readthedocs.io/en/develop.


How it works
~~~~~~~~~~~~

Since Kubernetes lacks a autoscale system for Stateful Set pods, it is necessary to implement a new service to play this role. Overscaler may run externally or be deployed as a new Stateful Set within the cluster, in any case, permissions are required to access Kubernetes internal services.

Monitoring and autoscaling is based on Stateful Sets labels and each one should include a series of labels that define: 
	- Overscaler is On or Off for this Stateful Set
	- Metrics that will be monitored.
	- Rules that will be applied to rescale.

Periodically, Overscaler scans full cluster to obtain the Stateful Sets labels and, after checking them, starts monitoring each Pod.

During this monitoring, Overscaler realizes a set of GET requests to an internal Kubernete service called Heapster_ that returns metrics related to Pods status, and checks if any limit established by the rules is exceeded to rescale the respective Stateful Set. 

Usage
~~~~~~~~~~~~

Login and cluster credentials
------------

The first step is to login with gcloud and get the cluster credentials to monitor. To login run:

.. code-block:: console

	$ gcloud auth login

Or if you prefer to log in with a service account:

.. code-block:: console

	$ gcloud auth activate-service-account --key-file /path/to/credentials.json

For more information about gcloud login with visit login_

To get credentials run:

.. code-block:: console

	$ gcloud container clusters get-credentials CLUSTER_NAME --zone ZONE_NAME --project PROJECT_NAME

Run Overscaler
---------------

Usage: 

.. code-block:: console

	$ overscaler start [OPTIONS]


Start Overscaler to monitor and autoscale.

Monitoring and autoscaling are based on labels. Each Stateful Set must
include a series of labels that define:
	- Overscaler is On or Off for this Stateful Set.
  	- Metrics that will be monitored.
  	- Rules that will be applied to rescale.

Options:
  -pr, --project TEXT            Project name.  [required]
  -c, --cluster TEXT             Cluster name.  [required]
  -z, --zone TEXT                Project zone name  [required]
  -n, --namespace TEXT           Cluster namespace, default to "default".
  --refresh_cluster INTEGER      Refresh period for cluster labels (seconds).
                                 Default to 600.
  --refresh_statefulset INTEGER  Refresh period for stateful set labels
                                 (seconds). 
                                 Default to 300. (seconds).
  --refresh_auth INTEGER         Refresh period for Api authentication
                                 (seconds). 
                                 Default to 300. (seconds).
  --help                         Show this message and exit.




Credits
~~~~~~~~~~~~

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _login: https://cloud.google.com/sdk/gcloud/reference/auth/login
.. _Heapster: https://github.com/kubernetes/heapster
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

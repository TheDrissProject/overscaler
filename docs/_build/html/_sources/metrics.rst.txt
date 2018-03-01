.. highlight:: shell

============
Labels
============

As already mentioned this system is based on labels to know what metrics to get and what rules to apply. This labels must be written in spec.template.metadata.labels within the deployment yaml file.

Overscaler labels
~~~~~~~~

In addition to metrics and rules it is also necessary to add some extra labels for the correct operation of the system.

	- app: Stateful Set name.
	- overscaler: "true" or “false”, active or deactivate overscaler in this Stateful set.
	- current-count: Rescaling counter. During monitoring, this value is reduced until 0, then is possible to rescale.
	- autoscaler-count: Value to be assigned in "current-count" after rescaling.
	- min-replicas: Maximum number of replicas for this stateful set.
	- max-replicas: Minimum number of replicas for this stateful set.
	- rescaling: Flag to know when a Stateful Set is being rescaled.

Current-count and autoscaler-count labels play a key role. Each type of service requires a certain time after start to configure and start working in parallel with the other replicas. With these labels we guarantee that time.

Metrics
~~~~~

Overscaler is designed for a customizable monitoring through labels, adding a label for each metric to monitor, and there are different sets of node and pod metrics. 

Label format:

		metric-n: "metric-name"

Example::

		metric-1: "cpu-usage-percent"

However, it is still possible to monitor the entire node or pod using the label "all-metrics: true".

Node metrics
------------

These metrics determine the status of the different nodes and are assigned by labels in the Google Kubernetes Engine.

.. table:: Node metrics
   :widths: auto

   ==================================  =====================================================================
   Metric Name				Description
   ==================================  =====================================================================
   cpu-limit				Cpu hard limit in millicores.
   cpu-node-capacity			Cpu capacity of a node.
   cpu-node-allocatable			Cpu allocatable of a node.
   cpu-node-reservation			Share of cpu that is reserved on the node allocatable.
   cpu-node-utilization			Cpu utilization as a share of node allocatable.
   cpu-request				Cpu request (the guaranteed amount of resources) in millicores.
   cpu-usage				Cumulative cpu usage on all cores.
   cpu-usage-rate			Cpu usage on all cores in millicores.
   cpu-usage-percent			Cpu usage percent of total cpu Node.
   memory-limit				Memory hard limit in bytes.
   memory-major-page-faults		Number of major page faults.
   memory-major-page-faults-rate	Number of major page faults per second.
   memory-node-capacity			Memory capacity of a node.
   memory-node-allocatable		Memory allocatable of a node.
   memory-node-reservation		Share of memory that is reserved on the node allocatable.
   memory-node-utilization		Memory utilization as a share of memory allocatable.
   memory-page-faults			Number of page faults.
   memory-page-faults-rate		Number of page faults per second.
   memory-request			Memory request (the guaranteed amount of resources) in bytes.
   memory-usage				Total memory usage.
   memory-rss				RSS memory usage.
   memory-working-set			Total working set usage. Working set is the memory being used and not easily dropped by the    kernel.
   memory-usage-percent			Memory usage percent of total memory Node.
   network-rx				Cumulative number of bytes received over the network.
   network-rx-errors			Cumulative number of errors while receiving over the network.
   network-rx-errors-rate		Number of errors while receiving over the network per second.
   network-rx-rate			Number of bytes received over the network per second.
   network-tx				Cumulative number of bytes sent over the network
   network-tx-errors			Cumulative number of errors while sending over the network
   network-tx-errors-rate		Number of errors while sending over the network
   network-tx-rate			Number of bytes sent over the network per second.
   uptime				Number of milliseconds since the container was started.
   ==================================  =====================================================================


Pod metrics
------------

These metrics determine the status of any Pods and are assigned by labels in the different Stateful sets.

.. table:: Pod metrics
   :widths: auto

   ==================================  =====================================================================
   Metric Name				Description
   ==================================  =====================================================================
   cpu-limit				Cpu hard limit in millicores.
   cpu-request				Cpu request (the guaranteed amount of resources) in millicores.
   cpu-usage-rate			Cpu usage on all cores in millicores.
   cpu-usage-percent			Cpu usage percent of total node cpu.
   memory-limit				Memory hard limit in bytes.
   memory-major-page-faults-rate	Number of major page faults per second.
   memory-page-faults-rate		Number of page faults per second.
   memory-request			Memory request (the guaranteed amount of resources) in bytes.
   memory-usage				Total memory usage.
   memory-rss				RSS memory usage.
   memory-working-set			Total working set usage. Working set is the memory being used and not easily dropped by the kernel.
   memory-usage-percent			Memory usage percent of total node memory.
   network-rx				Cumulative number of bytes received over the network.
   network-rx-errors			Cumulative number of errors while receiving over the network.
   network-rx-errors-rate		Number of errors while receiving over the network per second.
   network-rx-rate			Number of bytes received over the network per second.
   network-tx				Cumulative number of bytes sent over the network
   network-tx-errors			Cumulative number of errors while sending over the network
   network-tx-errors-rate		Number of errors while sending over the network
   network-tx-rate			Number of bytes sent over the network per second.
   uptime				Number of milliseconds since the container was started.
   ==================================  =====================================================================


Rules
~~~~~~~~~~

The rules for scaling are also assigned by labels and must have a specific syntax:

Label format:

		rule-n: “metric_greater|lower_limit_scale|reduce”

	- metric: Previously established metrics.
	- greater or lower: “>” or “<” that limit.
	- limit: Number that establishes a limit
	- scale or reduce: Action to be realized when the limit is exceeded.

Example::

		rule-1: "cpu-usage-percent_greater_90_scale"
		rule-2: "memory-usage-percent_greater_90_scale"
		rule-3: "cpu-usage-percent_lower_10_reduce"
		rule-4: "memory-usage-percent_lower_10_reduce"


.. labels_end




.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/
.. _Github repo: https://github.com/GleamAI/overscaler

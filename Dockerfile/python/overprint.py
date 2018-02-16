from time import gmtime, strftime

# Print Functions.

def print_cluster_info(autoscale,current_nodes, max_nodes,min_nodes,overscaler,metrics):
    """
    Prints Cluster information by console.

    Arguments:
    - autoscale: True if the node autoscale is active. (boolean)
    - current_nodes: Number of current nodes. (int)
    - max_nodes: Maximum number of allowed nodes. (int)
    - min_nodes: Minimum number of allowed nodes. (int)
    - overscaler: True if the node overscale is active. (boolean) NOT IMPLEMENTED
    - metrics: List of cluster metrics to monitor. (string array)
    - rules: List of cluster rules for node autoscale. (string array) NOT IMPLEMENTED
    """

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Autoscaler is " + str(autoscale) + " in this cluster")
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Maximum possible nodes: " + str(max_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Minimum possible nodes: " + str(min_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Nodes currently running: " + str(current_nodes))
    if metrics:
        for i in range(len(metrics)):
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER METRICS] Metric " + str(i + 1) + ": " + str(
                metrics[i]))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Overscaler is " + str(overscaler) + " in this cluster")
    # if overscaler == True:
    #     if rules:
    #         for i in range(len(rules)):
    #             print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER RULES] Rule " + str(i + 1) + ": " + str(
    #                 rules[i]).replace("_", " "))


def print_statefulset_info(statefulset_labels):
    """
    Prints Stateful Set information by console.

    Arguments:
    - statefulset_lables: Dict with metrics and rules of each stateful set. (dict)
    """

    for i in list(statefulset_labels.keys()):
        if len(statefulset_labels[i]["metrics"]) > 0:
            for j in range(len(statefulset_labels[i]["metrics"])):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD METRICS] Metric " + str(j + 1) + " for "+str(i) +": " + str(statefulset_labels[i]["metrics"][j]))
        if len(statefulset_labels[i]["rules"]) > 0:
            for j in range(len(statefulset_labels[i]["rules"])):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD RULES] Rule " + str(j + 1) + " for "+str(i) +": " \
                  + str(statefulset_labels[i]["rules"][j].replace("_", " ")))


def print_node_status(node_status):
    """
    Prints Node status by console.

    Arguments:
    - node_status: Dictionary with all the information about the status of each node. (dict)
    """
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Node Status:")
    for i in list(node_status.keys()):
        for j in list(node_status[i].keys()):
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [NODE STATUS] Node " +str(i)+ " " +str(j)+" : " +str(node_status[i][j]))


def print_pod_status(pod_status):
    """
    Prints Pod status by console.

    Arguments:
    - pod_status: Dictionary with all the information about the status of each pod. (dict)
    """
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Pods Status:")
    for i in list(pod_status.keys()):
        for j in list(pod_status[i].keys()):
            for k in list(pod_status[i][j]):
                print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [POD STATUS] Node " +str(i)+ " Pod " +str(j)+ ": " +str(k)+"= " +str(pod_status[i][j][k]))

from time import gmtime, strftime

# Print Functions.

def print_cluster_info(autoscale,current_nodes, max_nodes,min_nodes,metrics):
    """
    Prints Cluster information by console.

    Arguments:
    - autoscale: True if the node autoscale is active. (boolean)
    - current_nodes: Number of current nodes. (int)
    - max_nodes: Maximum number of allowed nodes. (int)
    - min_nodes: Minimum number of allowed nodes. (int)
    - metrics: List of cluster metrics to monitor. (string array)
    """

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Autoscaler is " + str(autoscale) + " in this cluster")
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Maximum possible nodes: " + str(max_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Minimum possible nodes: " + str(min_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Nodes currently running: " + str(current_nodes))

    if metrics:
        cont=1
        for i in metrics:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER METRICS] Metric " + str(cont) + ": " + i)
            cont+=1

    # print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Overscaler is " + str(overscaler) + " in this cluster")
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
    for i in statefulset_labels:
        if statefulset_labels[i]["metrics"]:
            cont=1
            for j in statefulset_labels[i]["metrics"]:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD METRICS] Metric " +str(cont)+ " for "+i +": " + j)
                cont+=1
        if statefulset_labels[i]["rules"]:
            cont=1
            for j in statefulset_labels[i]["rules"]:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD RULES] Rule " + str(cont) + " for "+i +": " \
                      + j.replace("_", " "))
                cont+=1


def print_node_status(node_status):
    """
    Prints Node status by console.

    Arguments:
    - node_status: Dictionary with all the information about the status of each node. (dict)
    """
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Node Status:")
    for i in node_status:
        for j in node_status[i]:
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [NODE STATUS] Node " +i+ " " +j+" : " +str(node_status[i][j]))


def print_pod_status(pod_status):
    """
    Prints Pod status by console.

    Arguments:
    - pod_status: Dictionary with all the information about the status of each pod. (dict)
    """
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Pods Status:")
    for i in pod_status:
        for j in pod_status[i]:
            for k in pod_status[i][j]:
                print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [POD STATUS] Node " +i+ " Pod " +j+ ": " +k+"= " +str(pod_status[i][j][k]))

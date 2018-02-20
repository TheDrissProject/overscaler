import subprocess
import requests
import time
import json
import operator
import pykube
from time import gmtime, strftime
import re
import argparse
import numpy as np

# JSON files with available metrics
standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))



# Auxiliary Functions.

def get_args():
    """
    Parses arguments

    Output:
    - args: Arguments. (argparse.Namespace)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("--cluster", help="Cluster name")
    parser.add_argument("--namespace", help="Cluster namespace")
    parser.add_argument("--project", help="Project name", required=True)
    parser.add_argument("--zone", help="Zone name", required=True)
    parser.add_argument("--refresh_cluster", help="Refresh period for cluster labels. (seconds)")
    parser.add_argument("--refresh_statefulset", help="Refresh period for stateful set labels. (seconds)")
    parser.add_argument("--refresh_auth", help="Refresh period for Api authentication. (seconds)")
    args = parser.parse_args()

    if args.namespace==None:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [Error] \"--namespace\" is None, changed to \"default\"")
        args.namespace="default"
    if args.refresh_cluster==None or not str(args.refresh_cluster).isdigit():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [Error] \"--refresh_cluster\" is None or not digit, changed to 600")
        args.refresh_cluster=600
    if args.refresh_statefulset==None or not str(args.refresh_statefulset).isdigit():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [Error] \"--refresh_statefulset\" is None or not digit, changed to 300")
        args.refresh_statefulset=300
    if args.refresh_auth==None or not str(args.refresh_auth).isdigit():
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [Error] \"--refresh_auth\" is None or not digit, changed to 600")
        args.refresh_auth=600

    return args



def start_proxy():
    """
    Starts local proxy to Kubernetes cluster.
    host: 127.0.0.1:8001
    """

    bash_proxy = "kubectl proxy &"
    subprocess.call(['bash', '-c', bash_proxy])

    time.sleep(2)



def check_rule(rule,type):
    """
    Checks the rules are well written.
    Format rule: metric_greater|lower_limit_scale|reduce|and_*

    Arguments:
    - rule: Rule to check. (string)
    - type: Rule type, can be for node or pod

    Output:
    - check: True if the rule has correct format. (boolean)
    """

    rule=rule.split("_")
    check = False
    if type=="pod":
        if len(rule)==4 and rule[0] in standard_pod_metrics \
            and (rule[1]=="greater" or rule[1]=="lower") and rule[2].isdigit()\
            and (rule[3]=="scale" or rule[3]=="reduce") :
                 # or len(list(filter(re.compile("and-.*").search, list(rule[3])))) > 0):
                check=True
    if type=="node":
        if len(rule)==4 and rule[0] in standard_node_metrics \
            and (rule[1]=="greater" or rule[1]=="lower") and rule[2].isdigit()\
            and (rule[3]=="scale" or rule[3]=="reduce") :
            #len(list(filter(re.compile("and-.*").search, list(rule[3])))) > 0):
                check=True
    return check


def get_num_nodes():
    """
    Returns number of active nodes.

    Output:
    - num_nodes: Number of current nodes. (int)
    """

    try:
        num_nodes=len(requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json())
    except:
        print(strftime("%Y-%m-%d %H:%M:%S",
                       gmtime()) + " [ERROR] Error to get active nodes.")
        num_nodes=0

    return num_nodes

def get_mean(metric):
    """
    Calculates the arithmetic mean of a metric.

    Output:
    - mean: arithmetic mean. (float)
    """

    mean=0
    cont=0
    for i in metric:
        if isinstance(i,dict) and 'value' in i and str(i['value']).isdigit():
            mean+=float(i['value'])
            cont+=1
    if cont > 0:
        mean=round(mean/cont, 2)

    return mean


# Get Labels Functions.


def get_cluster_labels(cluster_info):
    """
    Gets cluster information.

    Returns information about the number of nodes and their limits,
    node autoscale function and labels.

    Arguments:
    - cluster_info: Dictionary with all cluster information. (dict)

    Output:
    - autoscale: True if the node autoscale is active. (boolean)
    - max_nodes: Maximum number of allowed nodes. (int)
    - min_nodes: Minimum number of allowed nodes. (int)
    - metrics: List of cluster metrics to monitor. (string array)
    """

    metrics = []
    autoscale = False
    max_nodes = 0
    min_nodes= 0

#    rules = []
#    overscaler = False

    try:
        if isinstance(cluster_info["nodePools"][0]["autoscaling"]["enabled"],bool) \
            and cluster_info["nodePools"][0]["autoscaling"]["minNodeCount"]>0 \
            and cluster_info["nodePools"][0]["autoscaling"]["maxNodeCount"]>=cluster_info["nodePools"][0]["autoscaling"]["minNodeCount"]:
            autoscale = cluster_info["nodePools"][0]["autoscaling"]["enabled"]
            max_nodes = int(cluster_info["nodePools"][0]["autoscaling"]["maxNodeCount"])
            min_nodes = int(cluster_info["nodePools"][0]["autoscaling"]["minNodeCount"])

            if "all-metrics" in cluster_info["resourceLabels"] and \
                cluster_info["resourceLabels"]["all-metrics"].lower()=="true":
                metrics=list(standard_node_metrics.keys())

            else:
                for i in list(filter(re.compile("metric-.*").search, cluster_info["resourceLabels"])):
                    if cluster_info["resourceLabels"][i] in list(standard_node_metrics.keys()):
                        metrics.append(cluster_info["resourceLabels"][i])
                    else:
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Wrong value for " + str(i))

#            if "overscaler" in list(cluster_info["resourceLabels"].keys())\
#                and cluster_info["resourceLabels"]["overscaler"] == "true":
#                overscaler = True

                # if len(list(filter(re.compile("rule-.*").search, list(cluster_info["resourceLabels"].keys())))) > 0:
                #     for i in list(filter(re.compile("rule-.*").search, list(cluster_info["resourceLabels"].keys()))):
                #         rule = cluster_info["resourceLabels"][i]
                #         check=check_rule(rule,"node")
                #         if check:
                #             rules.append(rule)
                #         else:
                #             print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Wrong built rule: " +str(rule))
                # else:
                #     print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Cluster labels without rules or with rules incorrectly created.")

    except:
        metrics = []
        autoscale = False
        max_nodes = 0
        min_nodes = 0
#        rules = []
#        overscaler = False
        print(strftime("%Y-%m-%d %H:%M:%S",
                       gmtime()) + " [ERROR] Cluster without labels or with labels incorrectly created.")


#    return autoscale, max_nodes,min_nodes, overscaler, metrics, rules
    return autoscale, max_nodes,min_nodes, metrics


def get_statefulset_labels(statefulset_info):
    """
    Gets Stateful Set information.
    Returns information about labels, metrics and rules.

    Arguments:
    - statefulset_info: Dictionary with all Stateful Set information. (dict)

    Output:
    - statefulset_labels: Dictionary with only the information needed for the overscaler. (dict)

    Dict Format:
    {
    statefulset_name1:{
        overscaler: true|false,            Is overscaler active? (boolean)
        current-count:number,              Autoscale pause counter. (int)
        autoscaler-count: number,          Number of waiting cycles after rescalling. (int)
        max-replicas: number,              Maximum number of replicas. (int)
        min-replicas: number,              Minimum number of replicas. (int)
        metrics: [metric1,metric2...],     List with all metrics to monitor. (string array)
        rules: [rule1,rule2...]            List with all rules for this Stateful Set. (string array)
        }
    statefulset_name2:{
        ...
        ....
        .....
        }
    ...
    ....
    .....
    }
    """

    statefulset_labels = {}
    try:
        for s in statefulset_info['items']:
            metrics = []
            rules = []
            overscaler = False
            current_count = 0
            autoscaler_count = 0
            max_replicas = 0
            min_replicas = 0
            try:
                name = s["metadata"]["name"]

                if "all-metrics" in s["metadata"]["labels"] and \
                s["metadata"]["labels"]["all-metrics"].lower() == "true":
                    metrics = list(standard_pod_metrics.keys())
                else:
                    for i in list(filter(re.compile("metric-.*").search, s["metadata"]["labels"])):
                        if s["metadata"]["labels"][i] in standard_pod_metrics:
                            metrics.append(s["metadata"]["labels"][i])
                        else:
                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Wrong value for " + i +" of Stateful Set "+name)

                try:
                    if s["metadata"]["labels"]["overscaler"] == "true" and int(s["metadata"]["labels"]["min-replicas"])>0  \
                        and int(s["metadata"]["labels"]["max-replicas"]) >= int(s["metadata"]["labels"]["min-replicas"]) \
                        and int(s["metadata"]["labels"]["autoscaler-count"])>=0 and int(s["metadata"]["labels"]["current-count"])>=0  \
                        and s["metadata"]["labels"]["rescaling"] in ["true","false"]:
                        overscaler = True
                        current_count = int(s["metadata"]["labels"]["current-count"])
                        autoscaler_count = int(s["metadata"]["labels"]["autoscaler-count"])
                        max_replicas = int(s["metadata"]["labels"]["max-replicas"])
                        min_replicas = int(s["metadata"]["labels"]["min-replicas"])

                        for i in list(filter(re.compile("rule-.*").search, s["metadata"]["labels"])):
                            rule = s["metadata"]["labels"][i]
                            check = check_rule(rule,"pod")
                            if check:
                                rules.append(rule)
                            else:
                                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Wrong value for " + i+" of Stateful Set "+name+": "+rule)

                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD] Stateful Set labels obtained correctly: " + name)

                    elif s["metadata"]["labels"]["overscaler"] != "true":
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Overscaler label is not true in "+name+". Autoscale off.")
                    else:
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Wrong value for overscaler labels of Stateful Set "+name+". Autoscale off.")
                except:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ERROR] Error to get labels for "+name+". Are all overscaler labels correctly written?")
                    rules=[]
                    overscaler = False
                    current_count = 0
                    autoscaler_count = 0
                    max_replicas = 0
                    min_replicas = 0

                if overscaler==True or metrics:
                    statefulset_labels[name] = {'overscaler': overscaler, 'current-count': current_count,
                                            'autoscaler-count': autoscaler_count, 'max-replicas': max_replicas,
                                            'min-replicas': min_replicas, 'metrics': metrics, 'rules': rules}
            except:
                print(strftime("%Y-%m-%d %H:%M:%S",
                               gmtime()) + " [ERROR] Stateful Set without name")
    except:
        print(strftime("%Y-%m-%d %H:%M:%S",
                       gmtime()) + " [ERROR] Stateful Set info empty")

    return statefulset_labels







# Get Status Functions.


def get_node_status(metrics):
    """
    Gets Node status.
    Returns information about state of all nodes.

    Arguments:
    - metrics: List of metrics to monitor. (string array)

    Output:
    - node_status: Dictionary with all the information. (dict)

    Dict Format:
    {
    node_name1:{
         metric-name1: number,            Value each metric. (int)
         metric-name2: number,
         ...
         ....
         .....
         }

    node2_name:{
         ...
         ....
         .....
         }
    ...
    ....
    .....
    }
    """


    try:
        nodes = requests.get(
            'http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json()
        node_status = {}

        max_node_memory = float(requests.get(
            'http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/' + nodes[0]+ '/metrics/memory/node_allocatable').json()["metrics"][0]["value"])
        max_node_cpu = float(requests.get(
            'http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/' + nodes[0] + '/metrics/cpu/node_allocatable').json()["metrics"][0]["value"])

        for i in nodes:
            status={}
            try:

                for j in metrics:
                    if j == "memory-usage-percent":
                        memory_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+i+'/metrics/memory/working_set').json()["metrics"]
                        status[j] = round(get_mean(memory_usage)/max_node_memory *100,2)
                    elif j == "cpu-usage-percent":
                        cpu_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+i+'/metrics/cpu/usage_rate').json()["metrics"]
                        status[j] = round(get_mean(cpu_usage)/max_node_cpu*100,2)
                    elif j in standard_node_metrics:
                        status[j] = get_mean(requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+i+'/metrics/'+standard_node_metrics[j]).json()["metrics"])
            except:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ERROR] Error to get status for node: " +i)
                status={}
            node_status[i]=status
    except:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to get status for cluster")
        node_status={}
        max_node_cpu=0
        max_node_memory=0
    return node_status, max_node_cpu, max_node_memory



def get_pod_status(api,namespace,statefulset_labels,memory_allocatable, cpu_allocatable):
    """
    Gets Pod status.
    Returns information about state of all stateful set pods.

    Arguments:
    - api: Http client for requests to Kubernetes Api. (pykube.http.HTTPClient)
    - namespace: Project namespace (string)
    - statefulset_lables: Dict with metrics for each stateful set. (dict)
    - memory_allocatable: Maximum memory allowed per node, expressed in bytes.(int)
    - cpu_allocatable: Maximum memory allowed per node, expressed in minicores. (int)

    Output:
    - pod_status: Dictionary with all the information. (dict)

    Dict Format:
    {
    node_name1:{
        pod-name1:{
            metric-name1: number,            Value each metric. (int|float)
            metric-name2: number,
            ...
            ....
            .....}
        pod-name2:{
            metric-name1: number,            Value each metric. (int|float)
            metric-name2: number,
            ...
            ....
            .....}
        }
    node2_name:{
         ...
         ....
         .....}
    }
    """
    pre_set = pykube.Pod.objects(api)

    pod_status = {}

    if statefulset_labels:
        try:
            for i in pre_set.response['items']:

                node_name = i['spec']['nodeName']
                pod_name=i['metadata']['name']
                if not node_name in pod_status.keys():
                    pod_status[node_name]={}
                if pod_name.rsplit("-",1)[0] in statefulset_labels:
                    metrics= statefulset_labels[pod_name.rsplit("-",1)[0]]['metrics']
                    status={}
                    for j in metrics:
                        try:
                            if j == "memory-usage-percent":
                                memory_usage = requests.get("http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/"+namespace+"/pods/" + pod_name + "/metrics/memory/working_set").json()["metrics"]
                                status[j] = round(get_mean(memory_usage) / memory_allocatable * 100, 2)
                            elif j == "cpu-usage-percent":
                                cpu_usage = requests.get("http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/"+namespace+"/pods/" + pod_name + "/metrics/cpu/usage_rate").json()["metrics"]
                                status[j] = round(get_mean(cpu_usage) / cpu_allocatable * 100, 2)
                            elif j in standard_pod_metrics:
                                status[j]=get_mean(requests.get("http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/"+namespace+"/pods/" + pod_name + "/metrics/"+standard_pod_metrics[j]).json()["metrics"])
                        except:
                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to get status for: "+pod_name)
                            status={}
                    pod_status[node_name][pod_name]=status
        except:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to get status pods.")

    return pod_status









# Actions functios.



def actions(api,namespace, pod_status, statefulset_labels, max_nodes):
    """
    Decision making based on pods status and stateful set rules.

    Arguments:
    - api: Http client for requests to Kubernetes Api. (pykube.http.HTTPClient)
    - namespace: Project namespace (string)
    - pod_status: Dictionary with status pod information. (dict)
    - statefulset_lables: Dict with metrics and rules of each stateful set. (dict)
    - max_nodes: Maximum number of allowed nodes. (int)
    """

    for i in pod_status:
        for j in pod_status[i]:
            statefulset_name=j.rsplit("-",1)[0]
            if statefulset_name in statefulset_labels and \
                statefulset_labels[statefulset_name]['overscaler']==True:

                try:
                    pre_set = pykube.StatefulSet.objects(api).filter(namespace=namespace).get(name=statefulset_name)
                    if int(pre_set.labels["current-count"])==0 and pre_set.labels["rescaling"]=="false":
                        for k in statefulset_labels[statefulset_name]['rules']:
                            if k.split("_")[0] in pod_status[i][j]:
                                action=None
                                if k.split("_")[1] == "greater":
                                    if float(pod_status[i][j][k.split("_")[0]]) >= float(k.split("_")[2]):
                                        if k.split("_")[3] == "scale":
                                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Is necessary to scale " + j + " for rule: " + k.replace("_", " "))
                                            action="scale"
                                        if k.split("_")[3] == "reduce":
                                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Is necessary to reduce " + j + " for rule: " + k.replace("_", " "))
                                            action="reduce"
                                if k.split("_")[1] == "lower":
                                    if float(pod_status[i][j][k.split("_")[0]]) <= float(k.split("_")[2]):
                                        if k.split("_")[3] == "scale":
                                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Is necessary to scale " + j + " for rule: " + k.replace("_", " "))
                                            action = "scale"
                                        if k.split("_")[3] == "reduce":
                                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Is necessary to reduce " + j + " for rule: " + k.replace("_", " "))
                                            action = "reduce"

                                rescale(api, namespace, statefulset_name, action,max_nodes)
                except:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to make decissions for: "+statefulset_name)


def rescale(api,namespace,statefulset_name,action,max_nodes):
    """
    Sets a new number of replicas for a given stateful set.

    Arguments:
    - api: Http client for requests to Kubernetes Api. (pykube.http.HTTPClient)
    - namespace: Project namespace (string)
    - statefulset_name: Name of the statefulset to be rescaled. (dict)
    - action: Action to be realized. Can be "rescale" o "reduce",one pods more or one pod less, respectively. (string)
    - max_nodes: Maximum number of allowed nodes. (int).
    """

    try:
        pre_set = pykube.StatefulSet.objects(api).filter(namespace=namespace).get(name=statefulset_name)

        if action is "scale" and pre_set.replicas<max_nodes and pre_set.replicas<int(pre_set.labels['max-replicas']):
            pre_set.replicas=pre_set.replicas+1
            pre_set.labels["rescaling"]="true"
            pre_set.update()
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling " + statefulset_name + "... ")
        elif action is "reduce" and pre_set.replicas>1 and pre_set.replicas>int(pre_set.labels['min-replicas']):
            pre_set.replicas=pre_set.replicas-1
            pre_set.labels["rescaling"]="true"
            pre_set.update()
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling " + statefulset_name + "... ")
        elif pre_set.replicas==1:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling not possible, there is only one replica for "+statefulset_name)
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Resizing for "+statefulset_name+" is failed")
        elif pre_set.replicas>=max_nodes:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling not possible, maximum nodes reached")
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Resizing for "+statefulset_name+" is failed")
        elif pre_set.replicas >= int(pre_set.labels['max-replicas']):
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling not possible, maximum replicas reached for "+statefulset_name)
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Resizing for " + statefulset_name + " is failed")
        elif pre_set.replicas <= int(pre_set.labels['min-replicas']):
            print(strftime("%Y-%m-%d %H:%M:%S",
                       gmtime()) + " [ACTION] Rescaling not possible, minimum replicas reached for " + statefulset_name)
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Resizing for " + statefulset_name + " is failed")
    except:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to rescale for: " + statefulset_name)


def update_current_count(api,namespace,statefulsets_labels):
    """
    Updates the "current-count" label of all Stateful sets.
    If its value is 0, this stateful set is ready to be scaled if is necessary.

    Arguments:
    - api: Http client for requests to Kubernetes Api. (pykube.http.HTTPClient)
    - namespace: Project namespace (string)
    - statefulset_lables: Dict with metrics and rules of each stateful set. (dict)
    """

    for i in statefulsets_labels:
        if statefulsets_labels[i]['overscaler']==True:
            try:
                pre_set = pykube.StatefulSet.objects(api).filter(namespace=namespace,
                                                                 field_selector={"metadata.name": i})
                if pre_set.response["items"][0]["status"]["currentReplicas"]==pre_set.response["items"][0]["status"]["replicas"] and pre_set.response["items"][0]['metadata']['labels']['rescaling']!="false":
                    new_statefulset = pykube.StatefulSet.objects(api).filter(namespace=namespace).get(name=i)
                    new_statefulset.labels["rescaling"] = "false"
                    new_statefulset.labels["current-count"] = new_statefulset.labels["autoscaler-count"]
                    new_statefulset.update()
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] Rescaling for " + i + " is completed")
                if int(pre_set.response["items"][0]['metadata']['labels']['current-count'])>0 and pre_set.response["items"][0]['metadata']['labels']["rescaling"]=="false":
                    new_statefulset = pykube.StatefulSet.objects(api).filter(namespace=namespace).get(name=i)
                    new_statefulset.labels["current-count"]=str(int(new_statefulset.labels["current-count"])-1)
                    new_statefulset.update()
                    print(strftime("%Y-%m-%d %H:%M:%S",
                               gmtime()) + " [ACTION] Update current-count for " +i)
            except:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ERROR] Error to update \"current-count\"  for: " + i)

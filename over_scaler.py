import subprocess
import requests
import time
from ast import literal_eval
import pandas as pd
import json
import operator
import pykube
from time import gmtime, strftime


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

def get_autoscale():

    max_nodes = 0
    min_nodes= 0

    bash_describe = "gcloud container clusters describe --format=json cluster-gleam --zone europe-west2-a"

    output = str(subprocess.check_output(bash_describe, shell=True))
    output = json.loads(output.replace("\\n", "").replace("b\'", "").replace("\'", ""))

    autoscale = output["nodePools"][0]["autoscaling"]["enabled"]

    if str(autoscale) == "True":
        max_nodes = output["nodePools"][0]["autoscaling"]["maxNodeCount"]
        min_nodes = output["nodePools"][0]["autoscaling"]["minNodeCount"]
    return autoscale, max_nodes,min_nodes

def get_num_nodes():
    return len(requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json())

def cluster_auth():
    bash_auth = "gcloud container clusters get-credentials cluster-gleam --zone europe-west2-a --project gleam-ai1"
    subprocess.check_output(['bash', '-c', bash_auth])

def start_proxy():
    bash_proxy = "kubectl proxy &"
    subprocess.call(['bash', '-c', bash_proxy])

    time.sleep(5)

def get_nodes_status():
    Nodes = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json()
    df_node_status = pd.DataFrame()

    for i in range(len(Nodes)):
        cpu_capacity = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/cpu/node_allocatable').json()
        memory_capacity = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/memory/node_allocatable').json()
        cpu_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/cpu/usage_rate').json()
        memory_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/memory/working_set').json()
        df_aux = pd.DataFrame({'name':str(Nodes[i]),'cpu_allocatable':int(cpu_capacity["metrics"][0]["value"]),'cpu_usage':int(cpu_usage["metrics"][0]["value"]),'cpu_usage_percent':round(cpu_usage["metrics"][0]["value"]/cpu_capacity["metrics"][0]["value"]*100,2),'memory_allocatable':int(memory_capacity["metrics"][0]["value"]),'memory_usage': int(memory_usage["metrics"][0]["value"]),'memory_usage_percent':round(memory_usage["metrics"][0]["value"]/memory_capacity["metrics"][0]["value"]*100,2)},index=[i])
        df_node_status=pd.concat([df_node_status,df_aux])
    return df_node_status

def get_pods_status(node_name, memory_capacity, cpu_capacity):
    Pods = str(
        subprocess.check_output("kubectl describe nodes "+str(node_name)+" | grep \"default \"",
                                 shell=True)).split("b'", 1)[1].split()

    df_pods_status = pd.DataFrame()
    for i in range(int(len(Pods)/10)):
        pod_memory_usage = requests.get(
                    "http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/default/pods/" + str(
                        Pods[i * 10 + 1]) + "/metrics/memory/working_set").json()
        pod_cpu_usage = requests.get(
                    "http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/default/pods/" + str(
                        Pods[i * 10 + 1]) + "/metrics/cpu/usage_rate").json()
        df_aux = pd.DataFrame({'node':str(node_name),'name':str(Pods[i * 10 + 1]),'cpu_usage': pod_cpu_usage["metrics"][0]["value"],
                                               'cpu_usage_percent': round(
                                                   pod_cpu_usage["metrics"][0]["value"] / int(cpu_capacity) * 100,
                                                   2),'memory_usage': pod_memory_usage["metrics"][0]["value"],
                                               'memory_usage_percent': round(
                                                   pod_memory_usage["metrics"][0]["value"] / memory_capacity * 100, 2)}, index=[i])
        df_pods_status = pd.concat([df_pods_status, df_aux])
    return df_pods_status

def get_labels(api,namespace):
    pre_set = pykube.StatefulSet.objects(api).filter(namespace=namespace)
    df_labels = pd.DataFrame()
    index=0
    for s in pre_set.response['items']:
        try:
            name = s["metadata"]["name"]
            autoscaler = s["metadata"]["labels"]["autoscaler"]
            autoscaler_percent_cpu = s["metadata"]["labels"]["autoscaler_percent_cpu"]
            autoscaler_percent_memory = s["metadata"]["labels"]["autoscaler_percent_memory"]
            autoreduce = s["metadata"]["labels"]["autoreduce"]
            autoreduce_percent_cpu = s["metadata"]["labels"]["autoreduce_percent_cpu"]
            autoreduce_percent_memory = s["metadata"]["labels"]["autoreduce_percent_memory"]
            current_count = s["metadata"]["labels"]["current_count"]
            autoscaler_count = s["metadata"]["labels"]["autoscaler_count"]
            min_replicas = s["metadata"]["labels"]["min_replicas"]
            max_replicas = s["metadata"]["labels"]["max_replicas"]

            if True:
                df_aux = pd.DataFrame(
                    {'name': str(name), 'autoscaler': autoscaler,'autoscaler_percent_cpu':autoscaler_percent_cpu,
                    'autoscaler_percent_memory':autoscaler_percent_memory,
                    'autoreduce': autoreduce, 'autoreduce_percent_cpu': autoreduce_percent_cpu,
                    'autoreduce_percent_memory': autoreduce_percent_memory,
                    'current_count': current_count, 'autoscaler_count':autoscaler_count,
                    'min_replicas':min_replicas,'max_replicas':max_replicas},index=[index])
                df_labels=pd.concat([df_labels,df_aux])
                index+=index
        except:
            print("[ERROR] Error to get labels for %s" % (s["metadata"]["name"]))


    return df_labels

def print_node_status(df_node_status):

    print("*" * 20)
    print("[STATUS_INFO] Node Status:")
    for i in range(len(df_node_status)):
        print("-" * 20)
        df_aux=df_node_status.iloc[i,:]
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] Node Name: " +str(df_aux["name"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] CPU allocatable (minicores): " +str(df_aux["cpu_allocatable"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] CPU usage (minicores): " +str(df_aux["cpu_usage"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] CPU usage (percent): " +str(df_aux["cpu_usage_percent"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] Memory allocatable (bytes): " +str(df_aux["memory_allocatable"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] Memory usage (bytes): " +str(df_aux["memory_usage"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] Memory usage (percent): " +str(df_aux["memory_usage_percent"]))
    print("*" * 20)

def print_pods_status(df_pods_status):

    print("=" * 20)
    print("[STATUS_INFO] Pods Status:")
    for i in range(len(df_pods_status)):
        print("-" * 20)
        df_aux=df_node_status.iloc[i,:]
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] Pod Name: " +str(df_aux["name"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] CPU usage (minicores): " +str(df_aux["cpu_usage"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] CPU usage (percent): " +str(df_aux["cpu_usage_percent"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] Memory usage (bytes): " +str(df_aux["memory_usage"]))
        print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] Memory usage (percent): " +str(df_aux["memory_usage_percent"]))
    print("=" * 20)



cluster_auth()
start_proxy()

autoscale, max_nodes,min_nodes = get_autoscale()

api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))



statefulset_labels=get_labels(api,"default")

cluster_labels=df_aux = {'autoscaler': autoscale,'autoscaler_percent_cpu':80,
                    'autoscaler_percent_memory':80,
                    'autoreduce': "true", 'autoreduce_percent_cpu': 10,
                    'autoreduce_percent_memory': 10,
                    'current_count': 0, 'autoscaler_count':10,
                    'min_nodes':min_nodes,'max_nodes':max_nodes}

current_nodes=get_num_nodes()

print()
print("Autoscaler is "+str(cluster_labels['autoscaler'])+" in this cluster")
print("Maximum possible nodes: " + str(cluster_labels['max_nodes']))
print("Minimum possible nodes: " + str(cluster_labels['min_nodes']))
print("Nodes currently running: " + str(current_nodes))
print("-" * 20)

while(True):
    df_node_status = get_nodes_status()
    print_node_status(df_node_status)
    print("-" * 20)
    for i in range(len(df_node_status['name'])):
        df_pods_status=get_pods_status(df_node_status['name'][i],df_node_status['memory_allocatable'][i],df_node_status['cpu_allocatable'][i])
        print("NODE: "+str(df_node_status['name'][i]))
        if df_pods_status.empty:
            print("Node without pods")
        else:
            print_pods_status(df_pods_status)
        print("-" * 20)



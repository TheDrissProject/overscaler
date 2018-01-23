import subprocess
import requests
import time
from ast import literal_eval
import pandas as pd
import json
import operator
import pykube
from time import gmtime, strftime
import re

standard_node_metrics = json.load(open('./node_metrics.json'))
standard_pod_metrics = json.load(open('./pod_metrics.json'))

def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text


def cluster_auth():
    bash_auth = "gcloud container clusters get-credentials cluster-gleam --zone europe-west2-a --project gleam-ai1"
    subprocess.check_output(['bash', '-c', bash_auth])

def start_proxy():
    bash_proxy = "kubectl proxy &"
    subprocess.call(['bash', '-c', bash_proxy])

    time.sleep(5)

def check_rule(rule):
    rule=rule.split("_")
    if len(rule)==4 and rule[0] in list(standard_pod_metrics.keys())\
        and (rule[1]=="greater" or rule[1]=="lower") and rule[2].isdigit()\
        and (rule[3]=="scale" or rule[3]=="reduce" or\
        len(list(filter(re.compile("and-.*").search, list(rule[3])))) > 0):
        check="right_rule"
    else:
        check="wrong_rule"
    return check

def check_metric(metric):
    metric=metric.split("_")
    if len(metric)==2:
        check="right_metric"
    else:
        check="wrong_metric"
    return check

def node_actions(status, rules,name,kind):
    if len(rules) > 0:
        for j in range(len(rules)):
            if str(rules[j]).split("_")[1] == "greater":
                if float(status[str(rules[j]).split("_")[0]]) > float(str(rules[j]).split("_")[2]):
                    if str(rules[j]).split("_")[3] == "scale":
                        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [ACTION] IS NECESSARY TO SCALE THE "+str(kind)+": " + str(name) + " for rule: " + str(rules[j]).replace("_", " "))
                    if str(rules[j]).split("_")[3] == "reduce":
                        print(strftime("%Y-%m-%d %H:%M:%S",
                                       gmtime()) + " [ACTION] IS NECESSARY TO REDUCE THE "+str(kind)+": " + str(name)+ " for rule: " + str(rules[j]).replace("_", " "))
            if str(rules[j]).split("_")[1] == "lower":
                if float(status[str(rules[j]).split("_")[0]]) < float(str(rules[j]).split("_")[2]):
                    if str(rules[j]).split("_")[3] == "scale":
                        print(strftime("%Y-%m-%d %H:%M:%S",
                                       gmtime()) + " [ACTION] IS NECESSARY TO SCALE THE "+str(kind)+": " + str(name)+ " for rule: " + str(rules[j]).replace("_", " "))
                    if str(rules[j]).split("_")[3] == "reduce":
                        print(strftime("%Y-%m-%d %H:%M:%S",
                                       gmtime()) + " [ACTION] IS NECESSARY TO REDUCE THE "+str(kind)+": " + str(name)+ " for rule: " + str(rules[j]).replace("_", " "))


def get_cluster_labels():

    max_nodes = 0
    min_nodes= 0

    bash_describe = "gcloud container clusters describe --format=json cluster-gleam --zone europe-west2-a --project gleam-ai1"

    output = str(subprocess.check_output(bash_describe, shell=True))
    output = json.loads(output.replace("\\n", "").replace("b\'", "").replace("\'", ""))

    autoscale = output["nodePools"][0]["autoscaling"]["enabled"]
    metrics = []
    rules=[]
    overscaler = "false"
    if "all-metrics" in list(output["resourceLabels"].keys()):
        if output["resourceLabels"]["all-metrics"].lower()=="true":
            metrics=list(standard_node_metrics.keys())
    elif len(list(filter(re.compile("metric-.*").search, list(output["resourceLabels"].keys())))) > 0:
        for i in list(filter(re.compile("metric-.*").search, list(output["resourceLabels"].keys()))):
            if output["resourceLabels"][i] in list(standard_node_metrics.keys()):
                metric = output["resourceLabels"][i]
                check=check_metric(metric)
                if check=="right_metric":
                    metrics.append(metric)
                else:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "[ERROR] Wrong written metrics: " +str(rule))
            else:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "[ERROR] Wrong value for " + str(i))

    if "overscaler" in output["resourceLabels"].keys() and output["resourceLabels"]["overscaler"] == "true":
        overscaler = output["resourceLabels"]["overscaler"]
        if len(list(filter(re.compile("rule-.*").search, list(output["resourceLabels"].keys())))) > 0:
            for i in list(filter(re.compile("rule-.*").search, list(output["resourceLabels"].keys()))):
                rule = output["resourceLabels"][i]
                check=check_rule(rule)
                if check=="right_rule":
                    rules.append(rule)
                else:
                    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "[ERROR] Wrong built rule: " +str(rule))

    if str(autoscale) == "True":
        max_nodes = output["nodePools"][0]["autoscaling"]["maxNodeCount"]
        min_nodes = output["nodePools"][0]["autoscaling"]["minNodeCount"]

    return autoscale, max_nodes,min_nodes, overscaler, metrics, rules

def get_num_nodes():
    return len(requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json())


def get_nodes_status(metrics,standart_metrics):
    Nodes = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/').json()
    df_node_status = pd.DataFrame()
    for i in range(len(Nodes)):
        node_status={}
        memory_allocatable = requests.get(
            'http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/' + Nodes[
                i] + '/metrics/memory/node_allocatable').json()
        cpu_allocatable = requests.get(
            'http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/' + Nodes[
                i] + '/metrics/cpu/node_allocatable').json()
        for j in metrics:
            if j == "memory-usage-percent":
                memory_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/memory/working_set').json()
                node_status[j] = round(memory_usage["metrics"][0]["value"]/memory_allocatable["metrics"][0]["value"]*100,2)
            elif j == "cpu-usage-percent":
                cpu_usage = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/cpu/usage_rate').json()
                node_status[j] = round(cpu_usage["metrics"][0]["value"]/cpu_allocatable["metrics"][0]["value"]*100,2)
            elif j in standart_metrics.keys():
                node_status[j] = requests.get('http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/nodes/'+Nodes[i]+'/metrics/'+str(standart_metrics[j])).json()["metrics"][0]["value"]
        df_aux = pd.DataFrame({'name':str(Nodes[i]),'status':[node_status],'cpu_allocatable':cpu_allocatable["metrics"][0]["value"],'memory_allocatable':memory_allocatable["metrics"][0]["value"]}, index=[i])
        df_node_status=pd.concat([df_node_status,df_aux])
    return df_node_status

def get_pods_status(node_name, memory_allocatable, cpu_allocatable, statefulset_labels,standart_metrics):
    Pods = str(
        subprocess.check_output("kubectl describe nodes "+str(node_name)+" | grep \"default \"",
                                 shell=True)).split("b'", 1)[1].split()

    df_pods_status = pd.DataFrame()
    for i in range(int(len(Pods)/10)):
        metrics= statefulset_labels.loc[statefulset_labels['name'] == str(str(Pods[i * 10 + 1]).rsplit("-",1)[0])]['metrics']
        if not metrics.empty and len(metrics[0])!=0:
            pod_status = {}
            for j in metrics[0]:
                if j == "memory-usage-percent":
                    memory_usage = requests.get("http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/default/pods/" + str(
                            Pods[i * 10 + 1]) + "/metrics/memory/working_set").json()
                    pod_status[j] = round(
                    memory_usage["metrics"][0]["value"] / memory_allocatable * 100, 2)
                elif j == "cpu-usage-percent":
                    cpu_usage = requests.get(
                        "http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/default/pods/" + str(
                            Pods[i * 10 + 1]) + "/metrics/cpu/usage_rate").json()
                    pod_status[j] = round(
                        cpu_usage["metrics"][0]["value"] / cpu_allocatable * 100, 2)
                elif j in standart_metrics.keys():
                    get_metric=requests.get(
                        "http://localhost:8001/api/v1/namespaces/kube-system/services/heapster/proxy/api/v1/model/namespaces/default/pods/" + str(
                            Pods[i * 10 + 1]) + "/metrics/"+str(standart_metrics[j])).json()
                    if len(get_metric["metrics"])!=0:
                        pod_status[j] =get_metric["metrics"][0]["value"]
            df_aux = pd.DataFrame({'node':str(node_name),'pod':str(Pods[i * 10 + 1]),'status':[pod_status]}, index=[i])
            df_pods_status = pd.concat([df_pods_status, df_aux])
    return df_pods_status

def get_statefulset_labels(api,namespace):
    pre_set = pykube.StatefulSet.objects(api).filter(namespace=namespace)
    df_labels = pd.DataFrame()
    index=0
    metrics = []
    rules = []

    for s in pre_set.response['items']:
        try:
            name = s["metadata"]["name"]
            if len(list(filter(re.compile("metric-.*").search,
                               list(s["metadata"]["labels"].keys())))) > 0:
                for i in list(filter(re.compile("metric-.*").search, list(s["metadata"]["labels"].keys()))):
                    metric = s["metadata"]["labels"][i]
                    metrics.append(metric)
            overscaler = s["metadata"]["labels"]["overscaler"]
            if overscaler == "true":
                current_count = s["metadata"]["labels"]["current_count"]
                autoscaler_count = s["metadata"]["labels"]["autoscaler_count"]
                max_replicas = s["metadata"]["labels"]["max_replicas"]
                min_replicas = s["metadata"]["labels"]["min_replicas"]

                if len(list(filter(re.compile("rule-.*").search, list(s["metadata"]["labels"].keys())))) > 0:
                    for i in list(filter(re.compile("rule-.*").search, list(s["metadata"]["labels"].keys()))):
                        rule = s["metadata"]["labels"][i]
                        check = check_rule(rule)
                        if check == "right_rule":
                            rules.append(rule)
                        else:
                            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + "[ERROR] Wrong built rule: " + str(rule))
                df_aux = pd.DataFrame(
                    {'name': str(name),'overscaler':overscaler,'current_count':current_count,'autoscaler_count':autoscaler_count,'max_replicas':max_replicas,'min_replicas':min_replicas, 'metrics': [metrics],'rules':[rules]},index=[index])
                df_labels=pd.concat([df_labels,df_aux])
                index+=index
        except:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+"[ERROR] Error to get labels for %s" % (s["metadata"]["name"]))
    return df_labels


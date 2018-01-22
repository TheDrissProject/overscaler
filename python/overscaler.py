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

standart_nodes_metrics = json.load(open('./nodes_metrics.json'))
standart_pods_metrics = json.load(open('./pods_metrics.json'))

cluster_auth()
start_proxy()

autoscale, max_nodes,min_nodes,overscaler,metrics,rules = get_cluster_labels()

api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))



statefulset_labels=get_statefulset_labels(api,"default")

current_nodes=get_num_nodes()

print()
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Autoscaler is "+str(autoscale)+" in this cluster")
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Maximum possible nodes: " + str(max_nodes))
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Minimum possible nodes: " + str(min_nodes))
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Nodes currently running: " + str(current_nodes))
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Labels:")
if len(metrics)>0:
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Metrics")
    for i in range(len(metrics)):
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO METRICS] Metric "+str(i+1)+": "+str(metrics[i]))
print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Overscaler is "+str(overscaler)+" in this cluster")
if overscaler=="true":
    if len(rules)>0:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO] Rules")
        for i in range(len(rules)):
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [INFO RULES] Rule "+str(i+1)+": "+str(rules[i]).replace("-"," "))



while(True):
    df_node_status = get_nodes_status(metrics,standart_metrics)
    print_node_status(df_node_status)
    for i in range(len(df_node_status['name'])):
        node_status=df_node_status.loc[i,'status']
        if len(rules)>0:
            for j in range(len(rules)):
                if str(rules[j]).split("-")[1]=="greater":
                     if float(node_status[str(rules[j]).split("-")[0]])>float(str(rules[j]).split("-")[2]):
                         if str(rules[j]).split("-")[3]=="scale":
                             print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ACTION] IS NECESSARY TO SCALE THE NODE: " + str(df_node_status['name'][i]+" for rule: "+str(rules[j]).replace("-"," ")))
                         if str(rules[j]).split("-")[3]=="reduce":
                             print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ACTION] IS NECESSARY TO REDUCE THE NODE: " + str(df_node_status['name'][i]+" for rule: "+str(rules[j]).replace("-"," ")))
                if str(rules[j]).split("-")[1]=="lower":
                     if float(node_status[str(rules[j]).split("-")[0]])<float(str(rules[j]).split("-")[2]):
                         if str(rules[j]).split("-")[3]=="scale":
                             print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ACTION] IS NECESSARY TO SCALE THE NODE: " + str(df_node_status['name'][i]+" for rule: "+str(rules[j]).replace("-"," ")))
                         if str(rules[j]).split("-")[3]=="reduce":
                             print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [ACTION] IS NECESSARY TO REDUCE THE NODE: " + str(df_node_status['name'][i]+" for rule: "+str(rules[j]).replace("-"," ")))
    for i in range(len(df_node_status['name'])):
        df_pods_status=get_pods_status(df_node_status.loc[i,'name'],df_node_status.loc[i,'memory_allocatable'],df_node_status.loc[i,'cpu_allocatable'],statefulset_labels,standart_metrics)
        if df_pods_status.empty:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [WARNING] Node "+str(df_node_status['name'][i])+" without pods to monitor")
        else:
            print_pods_status(df_pods_status)

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


def print_info_cluster(autoscale, max_nodes,min_nodes,overscaler,metrics,rules,current_nodes):
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Autoscaler is " + str(autoscale) + " in this cluster")
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Maximum possible nodes: " + str(max_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Minimum possible nodes: " + str(min_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Nodes currently running: " + str(current_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Labels:")
    if len(metrics) > 0:
        print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Metrics")
        for i in range(len(metrics)):
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO METRICS] Metric " + str(i + 1) + ": " + str(
                metrics[i]))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Overscaler is " + str(overscaler) + " in this cluster")
    if overscaler == "true":
        if len(rules) > 0:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO] Rules")
            for i in range(len(rules)):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO RULES] Rule " + str(i + 1) + ": " + str(
                    rules[i]).replace("-", " "))

def print_node_status(df_node_status):


    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS_INFO] Node Status:")
    for i in range(len(df_node_status)):
        node_status=df_node_status.loc[i,'status']
        for j in node_status.keys():
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_NODE] Node " +str(df_node_status.iloc[i,:]['name']+ " " +str(j)+" : " +str(node_status[j])))


def print_pods_status(df_pods_status):

    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS_INFO] Pods Status:")
    for i in range(len(df_pods_status)):
        pod_status=df_pods_status.loc[i,'status']
        for j in pod_status.keys():
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [STATUS_POD] Node " +str(df_pods_status.iloc[i,:]['node']+ " Pod " +str(df_pods_status.iloc[i,:]['pod']+ " " +str(j)+" : " +str(pod_status[j]))))

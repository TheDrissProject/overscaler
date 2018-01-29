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

standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))


def print_cluster_info(autoscale, max_nodes,min_nodes,overscaler,metrics,rules,current_nodes):
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Autoscaler is " + str(autoscale) + " in this cluster")
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Maximum possible nodes: " + str(max_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Minimum possible nodes: " + str(min_nodes))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Nodes currently running: " + str(current_nodes))
    if len(metrics) > 0:
        for i in range(len(metrics)):
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER METRICS] Metric " + str(i + 1) + ": " + str(
                metrics[i]))
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER] Overscaler is " + str(overscaler) + " in this cluster")
    if overscaler == "true":
        if len(rules) > 0:
            for i in range(len(rules)):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO CLUSTER RULES] Rule " + str(i + 1) + ": " + str(
                    rules[i]).replace("_", " "))


def print_statefulset_info(statefulset_labels):
    for i in range(len(statefulset_labels)):
        if len(statefulset_labels.loc[i,"metrics"]) > 0:
            for j in range(len(statefulset_labels.loc[i,"metrics"])):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD METRICS] Metric " + str(j + 1) + " for "+str(statefulset_labels.loc[i,"name"]) +": " + str(str(statefulset_labels.loc[i,"metrics"][j]).replace("_", " ")))
        if len(statefulset_labels.loc[i,"rules"]) > 0:
            for j in range(len(statefulset_labels.loc[i,"rules"])):
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " [INFO POD RULES] Rule " + str(j + 1) + " for "+str(statefulset_labels.loc[i,"name"]) +": " \
                  + str(statefulset_labels.loc[i,"rules"][j]).replace("_", " "))


def print_node_status(df_node_status):


    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Node Status:")
    for i in range(len(df_node_status)):
        node_status=df_node_status.loc[i,'status']
        for j in node_status.keys():
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [NODE STATUS] Node " +str(df_node_status.iloc[i,:]['name']+ " " +str(j)+" : " +str(node_status[j])))


def print_pods_status(df_pods_status):
    print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [STATUS INFO] Pods Status:")
    for i in range(len(df_pods_status)):
        pod_status=df_pods_status.loc[i,'status']
        for j in pod_status.keys():
            print(str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))+" [POD STATUS] Node " +str(df_pods_status.iloc[i,:]['node']+ " Pod " +str(df_pods_status.iloc[i,:]['pod']+ " " +str(j)+" : " +str(pod_status[j]))))

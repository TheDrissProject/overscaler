# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python import overtools as ot
from python import overprint as op
import json


def test_print_cluster_info():
    lstDir = os.walk("Dockerfile/test/cluster_info_test/")
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root + file))
            op.print_cluster_info(test_json['output']['autoscale'], test_json['output']['min_nodes'],test_json['output']['max_nodes'],test_json['output']['min_nodes'],test_json['output']['metrics'])



def test_print_statefulset_info():
    lstDir = os.walk("Dockerfile/test/print_statefulset_test/")
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root + file))
            op.print_statefulset_info(test_json)

def test_print_node_status():
    lstDir = os.walk("Dockerfile/test/print_node_status_test/")
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root + file))
            op.print_node_status(test_json)


def test_print_pod_status():
    lstDir = os.walk("Dockerfile/test/print_pod_status_test/")
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root + file))
            op.print_pod_status(test_json)









































# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python import overtools as ot
import subprocess
import itertools
import json



# def test_arguments():
#     error=0
#     bash = "python3 ~/overscaler/Dockerfile/test/args.py"
#     if subprocess.call(['bash', '-c', bash])==2:
#         print("Succesful checked.")
#     else:
#         error=1
#     assert error==0
#     simbols = list("0123456789abcdefghijklmnopqrstuvwxyz!$%/()=?*^:.,@#~_")
#     error=0
#     for p in itertools.product(simbols, repeat=2):
#         a=str(p).replace("(", "").replace(")", "").replace("\'", "").replace(", ", "")
#         bash = "python3 ./Dockerfile/test/args.py --namespace="+a+" --zone="+a+" --project="+a+" --refresh_auth="+a+" --refresh_statefulset="+a+" --refresh_cluster="+a+""
#         if subprocess.call(['bash', '-c', bash]) != 0:
#             print("Error. Argument: "+a)
#             error=1
#     assert error==0
#
# def test_check_rule():
#     standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
#     standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))
#     simbols = list("0123456789abcdefghijklmnopqrstuvwxyz-_")
#     for p in itertools.product(simbols, repeat=2):
#         a=str(p).replace("(", "").replace(")", "").replace("\'", "").replace(", ", "")
#         assert ot.check_rule(a,"node") == False
#         assert ot.check_rule(a+"_lower","node") == False
#         assert ot.check_rule(a+"_lower_100","node") == False
#         assert ot.check_rule(a+"_lower_100_scale","node")==False
#         assert ot.check_rule(a+"_greater_100_scale","node")==False
#         assert ot.check_rule(a+"_lower_100_reduce","node")==False
#         assert ot.check_rule(a+"_greater_100_reduce","node")==False
#         assert ot.check_rule(a+"_low_100_scale","node")==False
#         assert ot.check_rule(a+"_great_100_scale","node")==False
#         assert ot.check_rule(a+"_lower_100_red","node")==False
#         assert ot.check_rule(a+"_greater_100_sca","node")==False
#         assert ot.check_rule(a,"pod") == False
#         assert ot.check_rule(a+"_lower","pod") == False
#         assert ot.check_rule(a+"_lower_100","pod") == False
#         assert ot.check_rule(a+"_lower_100_scale","pod")==False
#         assert ot.check_rule(a+"_greater_100_scale","pod")==False
#         assert ot.check_rule(a+"_lower_100_reduce","pod")==False
#         assert ot.check_rule(a+"_greater_100_reduce","pod")==False
#         assert ot.check_rule(a+"_low_100_scale","pod")==False
#         assert ot.check_rule(a+"_great_100_scale","pod")==False
#         assert ot.check_rule(a+"_lower_100_red","pod")==False
#         assert ot.check_rule(a+"_greater_100_sca","pod")==False
#     for a in standard_node_metrics.keys():
#         assert ot.check_rule(a + "_lower_100_scale","node") == True
#         assert ot.check_rule(a + "_greater_100_scale","node") == True
#         assert ot.check_rule(a + "_lower_100_reduce","node") == True
#         assert ot.check_rule(a + "_greater_100_reduce","node") == True
#     for a in standard_pod_metrics.keys():
#         assert ot.check_rule(a + "_lower_100_scale","pod") == True
#         assert ot.check_rule(a + "_greater_100_scale","pod") == True
#         assert ot.check_rule(a + "_lower_100_reduce","pod") == True
#         assert ot.check_rule(a + "_greater_100_reduce","pod") == True
#
# def test_get_mean():
#     assert ot.get_mean({})==0
#     assert ot.get_mean([{}])==0
#     assert ot.get_mean([1])==0
#     assert ot.get_mean(["k"])==0
#     assert ot.get_mean([[]])==0
#     assert ot.get_mean([{'value':0}])==0
#     assert ot.get_mean([{'value':3},{'value':-5},{'value':"7"},{'value':"string"}])==5
#     assert ot.get_mean([{'value':3},{'value':-5},{'value':{"lle":"7"}},{'value':"string"}])==3

def test_get_cluster_labels():
    lstDir = os.walk("Dockerfile/test/cluster_info_test/")
    for root, dirs, files in lstDir:
        for file in files:
            test_json = json.load(open(root+file))
            output_test = ot.get_cluster_labels(test_json['input'])
            assert test_json['output']['autoscale'] == output_test[0]
            assert test_json['output']['max_nodes'] == output_test[1]
            assert test_json['output']['min_nodes'] == output_test[2]
            assert test_json['output']['overscaler'] == output_test[3]



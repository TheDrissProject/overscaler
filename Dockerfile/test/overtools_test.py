# -*- coding: utf-8 -*-
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python import overtools as ot
import json


def test_check_rule():
    """
    Unit test for "check_rule()"

    """

    standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
    standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))

    for i in ["pod","node"]:

        assert ot.check_rule("", i) == False
        assert ot.check_rule("a_a_a_a", i) == False
        assert ot.check_rule("0_0_0_0", i) == False
        assert ot.check_rule("____", i) == False

        if i=="pod":
            standard_metrics=standard_pod_metrics
        else:
            standard_metrics = standard_node_metrics

        for j in standard_metrics:
            assert ot.check_rule(j,i) == False
            assert ot.check_rule(j+"_lower",i) == False
            assert ot.check_rule(j+"_lower_100",i) == False
            assert ot.check_rule(j+"_low_100_scale",i)==False
            assert ot.check_rule(j+"_great_100_scale",i)==False
            assert ot.check_rule(j+"_lower_100_red",i)==False
            assert ot.check_rule(j+"_greater_100_sca",i)==False
            assert ot.check_rule(j + "_lower_100_scale",i) == True
            assert ot.check_rule(j + "_greater_100_scale",i) == True
            assert ot.check_rule(j + "_lower_100_reduce",i) == True
            assert ot.check_rule(j + "_greater_100_reduce",i) == True


def test_get_mean():
    """
    Unit test for "get_mean()"

    """

    assert ot.get_mean({})==0
    assert ot.get_mean([{}])==0
    assert ot.get_mean([1])==0
    assert ot.get_mean(["k"])==0
    assert ot.get_mean([[]])==0
    assert ot.get_mean([{'value':0}])==0
    assert ot.get_mean([{'value':3},{'value':7}])==5
    assert ot.get_mean([{'value':3},{'value':7},{'value':-5}])==5
    assert ot.get_mean([{'value':3},{'value':"7"}])==5
    assert ot.get_mean([{'valu': 4}, {'value': -5}, {'value': "0"}]) == 0
    assert ot.get_mean([{'value':{"a": ''}},"", {'value': "7"}]) == 7
    assert ot.get_mean([{'value':4},{'value':-5},{'value':"0"}])==2
    assert ot.get_mean([{'value':''},{'value':"string"},{'value':"7"}])==7



def test_get_cluster_labels():
    """
    Unit test for "get_cluster_labels()"
    """

    standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
    lstDir = os.walk("Dockerfile/test/cluster_info_test/")
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root+file))
            output_test = ot.get_cluster_labels(test_json['input'])
            assert test_json['output']['autoscale'] == output_test[0]
            assert test_json['output']['max_nodes'] == output_test[1]
            assert test_json['output']['min_nodes'] == output_test[2]
            if test_json['output']['all-metrics']:
                for i in standard_node_metrics:
                    assert i in output_test[3]
            elif test_json['output']['metrics']:
                for i in test_json['output']['metrics']:
                    assert i in output_test[3]
            else:
                assert len(output_test[3])==0

def test_get_statefulset_labels():
    """
    Unit test for "get_statefulset_labels()"
    """

    lstDir = os.walk("Dockerfile/test/statefulset_info_test/")
    standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))
    for root, dirs, files in lstDir:
        for file in files:
            print(file)
            test_json = json.load(open(root+file))
            output_test = ot.get_statefulset_labels(test_json['input'])
            for i in test_json['output']:
                if i['empty']:
                    assert len(output_test.keys())==0
                else:
                    assert i['overscaler'] == output_test[i['name']]['overscaler']
                    assert i['current-count'] == output_test[i['name']]['current-count']
                    assert i['autoscaler-count'] == output_test[i['name']]['autoscaler-count']
                    assert i['max-replicas'] == output_test[i['name']]['max-replicas']
                    assert i['min-replicas'] == output_test[i['name']]['min-replicas']
                    for j in i['rules']:
                        assert j in output_test[i['name']]['rules']


                    if i['all-metrics']:
                        for j in list(standard_pod_metrics.keys()):
                            assert j in output_test[i['name']]['metrics']
                    elif i['metrics']:
                        print(i['metrics'])
                        for j in output_test[i['name']]['metrics']:
                            assert j in output_test[i['name']]['metrics']










































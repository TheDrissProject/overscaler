# -*- coding: utf-8 -*-
import os, sys
from overscaler import overtools as ot
import json
import subprocess
import unittest

# Auxiliary Functions.

def fixtures_path(file):
    relative_path = os.path.join('tests','fixtures',file)
    return os.path.abspath(relative_path)


def standard_metrics_path(file):
    relative_path = os.path.join('overscaler', file)
    return os.path.abspath(relative_path)




class TestOvertools(unittest.TestCase):
    """
    Subset of unit tests for "overtools.py"

    """

    def setUp(self):
        self.standard_node_metrics = json.load(open(standard_metrics_path('node_metrics.json')))
        self.standard_pod_metrics = json.load(open(standard_metrics_path('pod_metrics.json')))
        self.dir_fixtures_cluster = os.walk(fixtures_path('cluster_info') + '/')
        self.dir_fixtures_statefulset = os.walk(fixtures_path('statefulset_info') + '/')

    def test_check_rule(self):
        """
        Unit test for "check_rule()"

        """

        print()
        print("Test \"check_rule\"")

        for i in ["pod","node"]:

            assert ot.check_rule("", i) == False
            assert ot.check_rule("a_a_a_a", i) == False
            assert ot.check_rule("0_0_0_0", i) == False
            assert ot.check_rule("____", i) == False

            if i=="pod":
                standard_metrics=self.standard_pod_metrics
            else:
                standard_metrics = self.standard_node_metrics

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

    def test_get_mean(self):
        """
        Unit test for "get_mean()"

        """

        print()
        print("Test \"get_mean\"")

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

    def test_get_cluster_labels(self):
        """
        Unit test for "get_cluster_labels()"

        """

        print()
        print("Test \"get_cluster_labels\"")

        for root, dirs, files in self.dir_fixtures_cluster:
            for file in files:
                print("Test file: "+file)
                test_json = json.load(open(root+file))
                output_test = ot.get_cluster_labels(test_json['input'])
                assert test_json['output']['autoscale'] == output_test[0]
                assert test_json['output']['max_nodes'] == output_test[1]
                assert test_json['output']['min_nodes'] == output_test[2]
                if test_json['output']['all-metrics']:
                    for i in self.standard_node_metrics:
                        assert i in output_test[3]
                elif test_json['output']['metrics']:
                    for i in test_json['output']['metrics']:
                        assert i in output_test[3]
                else:
                    assert len(output_test[3])==0

    def test_get_statefulset_labels(self):
        """
        Unit test for "get_statefulset_labels()"

        """

        print()
        print("Test \"get_statefulset_labels\"")

        for root, dirs, files in self.dir_fixtures_statefulset:
            for file in files:
                print("Test file: "+file)
                test_json = json.load(open(root+file))
                output_test = ot.get_statefulset_labels(test_json['input'])
                for i in test_json['output']:
                    if i['empty']:
                        assert len(output_test.keys())==0

                    else:
                        assert i['overscaler'] == output_test[i['app']]['overscaler']
                        assert i['current-count'] == output_test[i['app']]['current-count']
                        assert i['autoscaler-count'] == output_test[i['app']]['autoscaler-count']
                        assert i['max-replicas'] == output_test[i['app']]['max-replicas']
                        assert i['min-replicas'] == output_test[i['app']]['min-replicas']
                        for j in i['rules']:
                            assert j in output_test[i['app']]['rules']

                        if i['all-metrics']:
                            for j in list(self.standard_pod_metrics):
                                assert j in output_test[i['app']]['metrics']

                        elif i['metrics']:
                            for j in output_test[i['app']]['metrics']:
                                assert j in output_test[i['app']]['metrics']










































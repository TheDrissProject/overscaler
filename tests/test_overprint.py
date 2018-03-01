# -*- coding: utf-8 -*-

import os, sys
from overscaler import overprint as op
import json
import unittest

# Auxiliary Functions.

def fixtures_path(file):
    relative_path = os.path.join('tests','fixtures',file)
    return os.path.abspath(relative_path)


class TestOverprint(unittest.TestCase):
    """
    Subset of unit tests for "overprint.py"

    """

    def setUp(self):
        self.dir_fixtures_cluster_info = os.walk(fixtures_path('cluster_info')+"/")
        self.dir_fixtures_statefulset_info = os.walk(fixtures_path('print_statefulset')+"/")
        self.dir_fixtures_node_status = os.walk(fixtures_path('print_node_status')+"/")
        self.dir_fixtures_pod_status = os.walk(fixtures_path('print_pod_status')+"/")

    def test_print_cluster_info(self):
        """
        Unit test for "print_cluster_info()"

        """
        print()
        print("Test print cluster")
        for root, dirs, files in self.dir_fixtures_cluster_info:
            for file in files:
                f=open(root+file)
                test_json = json.load(f)
                f.close()
                op.print_cluster_info(test_json['output']['autoscale'], test_json['output']['min_nodes'],test_json['output']['max_nodes'],test_json['output']['min_nodes'],test_json['output']['metrics'])

    def test_print_statefulset_info(self):
        """
        Unit test for "print_statefulset_info()"

        """
        print()
        print("Test print statefulset")
        for root, dirs, files in self.dir_fixtures_statefulset_info:
            for file in files:
                print(file)
                f=open(root+file)
                test_json = json.load(f)
                f.close()
                op.print_statefulset_info(test_json)


    def test_print_node_status(self):
        """
        Unit test for "print_node_status()"

        """
        print()
        print("Test print node status")
        for root, dirs, files in self.dir_fixtures_node_status:
            for file in files:
                print(file)
                f=open(root+file)
                test_json = json.load(f)
                f.close()
                op.print_node_status(test_json)

    def test_print_pod_status(self):
        """
        Unit test for "print_pod_status()"

        """
        print()
        print("Test print pod status")
        for root, dirs, files in self.dir_fixtures_pod_status:
            for file in files:
                print(file)
                f=open(root+file)
                test_json = json.load(f)
                f.close()
                op.print_pod_status(test_json)









































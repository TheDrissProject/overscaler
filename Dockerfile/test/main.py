import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from python import overtools as ot
import subprocess
import enchant
import itertools
import json



def test_arguments():
    error=0
    bash = "python3 ~/overscaler/Dockerfile/test/args.py"
    if subprocess.call(['bash', '-c', bash])==2:
        print("Succesful checked.")
    else:
        error=1
    assert error==0
    simbols = list("0123456789abcdefghijklmnopqrstuvwxyzºª!·$%/()=?¿*^Ç:.,ºª@#~½¬~-_")
    error=0
    for p in itertools.product(simbols, repeat=5):
        a=str(p).replace("(", "").replace(")", "").replace("\'", "").replace(", ", "")
        bash = "python3 ~/overscaler/Dockerfile/test/args.py --namespace="+a+" --zone="+a+" --project="+a+" --refresh_auth="+a+" --refresh_statefulset="+a+" --refresh_cluster="+a+""
        if subprocess.call(['bash', '-c', bash]) != 0:
            print("Error. Argument: "+a)
            error=1
    assert error==0

def test_check_rule():
    standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
    standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))
    simbols = list("0123456789abcdefghijklmnopqrstuvwxyz-_")
    for p in itertools.product(simbols, repeat=5):
        a=str(p).replace("(", "").replace(")", "").replace("\'", "").replace(", ", "")
        if not a in standard_pod_metrics.keys() and not a in standard_node_metrics.keys():
            assert ot.check_rule(a) == False
            assert ot.check_rule(a+"_lower") == False
            assert ot.check_rule(a+"_lower_100") == False
            assert ot.check_rule(a+"_lower_100_scale")==False
            assert ot.check_rule(a+"_greater_100_scale")==False
            assert ot.check_rule(a+"_lower_100_reduce")==False
            assert ot.check_rule(a+"_greater_100_reduce")==False
            assert ot.check_rule(a+"_low_100_scale")==False
            assert ot.check_rule(a+"_great_100_scale")==False
            assert ot.check_rule(a+"_lower_100_red")==False
            assert ot.check_rule(a+"_greater_100_sca")==False
    for a in standard_node_metrics:
        assert ot.check_rule(a + "_lower_100_scale") == True
        assert ot.check_rule(a + "_greater_100_scale") == True
        assert ot.check_rule(a + "_lower_100_reduce") == True
        assert ot.check_rule(a + "_greater_100_reduce") == True
    for a in standard_pod_metrics:
        assert ot.check_rule(a + "_lower_100_scale") == True
        assert ot.check_rule(a + "_greater_100_scale") == True
        assert ot.check_rule(a + "_lower_100_reduce") == True
        assert ot.check_rule(a + "_greater_100_reduce") == True

def test_get_mean():
    assert ot.get_mean({})==0
    assert ot.get_mean([{}])==0
    assert ot.get_mean([1])==0
    assert ot.get_mean([k])==0
    assert ot.get_mean([[]])==0
    assert ot.get_mean([{[{[{}]}]}])==0
    assert ot.get_mean([{'value':0}])==0
    assert ot.get_mean([{'value':3},{'value':-5},{'value':"7"},{'value':"string"}])==5
    assert ot.get_mean([{'value':3},{'value':-5},{'value':{"lle":"7"}},{'value':"string"}])==3

#def test_get_cluster_labels():
#    assert ot.get_cluster_labels("europe-west2-a","gleam-ai1")[0]== (True)

import json
import pykube
from time import gmtime, strftime
import overtools as ot
import overprint as op
import datetime



standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))

def main():

    ot.cluster_auth()
    ot.start_proxy()

    autoscale, max_nodes,min_nodes,overscaler,metrics,rules = ot.get_cluster_labels()
    api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))

    #api = pykube.HTTPClient(pykube.KubeConfig.from_service_account())

    statefulset_labels=ot.get_statefulset_labels(api,"default")

    current_nodes=ot.get_num_nodes()

    op.print_cluster_info(autoscale, max_nodes,min_nodes,overscaler,metrics,rules,current_nodes)
    op.print_statefulset_info(statefulset_labels)

    t_nodes=datetime.datetime.now()
    t_statefulset=datetime.datetime.now()
    while(True):

        t1=datetime.datetime.now()
        if (t1-t_nodes).seconds>600:
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))
            autoscale, max_nodes, min_nodes, overscaler, metrics, rules = ot.get_cluster_labels()
            current_nodes = ot.get_num_nodes()
            op.print_info_cluster(autoscale, max_nodes, min_nodes, overscaler, metrics, rules, current_nodes)
            t_nodes = datetime.datetime.now()

        t2=datetime.datetime.now()
        if (t2-t_statefulset).seconds>300:
            statefulset_labels = ot.get_statefulset_labels(api, "default")
            t_statefulset = datetime.datetime.now()

        df_node_status = ot.get_nodes_status(metrics,standard_node_metrics)
        op.print_node_status(df_node_status)

        for i in range(len(df_node_status['name'])):
            ot.actions(df_node_status.loc[i,'status'], rules,df_node_status.loc[i,'name'],"NODE")
        for i in range(len(df_node_status['name'])):
            df_pod_status=ot.get_pods_status(df_node_status.loc[i,'name'],df_node_status.loc[i,'memory_allocatable'],df_node_status.loc[i,'cpu_allocatable'],statefulset_labels,standard_pod_metrics)
            if df_pod_status.empty:
                print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [WARNING] Node "+str(df_node_status['name'][i])+" without pods to monitor")
            else:
                df_pod_status=df_pod_status.reset_index()
                op.print_pods_status(df_pod_status)
                for j in range(len(df_pod_status['pod'])):
                    ot.actions(df_pod_status.loc[j, 'status'], statefulset_labels.loc[statefulset_labels['name'] == str(df_pod_status.loc[j,'pod'])]["rules"], df_pod_status.loc[j, 'pod'],"POD")

if __name__ == '__main__':
    main()





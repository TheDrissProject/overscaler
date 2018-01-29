import json
import pykube
from time import gmtime, strftime
import overtools as ot
import overprint as op
import datetime



standard_node_metrics = json.load(open('/overscaler/python/node_metrics.json'))
standard_pod_metrics = json.load(open('/overscaler/python/pod_metrics.json'))

def main():

    args=ot.get_args()

    ot.cluster_auth(args.zone,args.project)
    ot.start_proxy()

    autoscale, max_nodes,min_nodes,overscaler,metrics,rules = ot.get_cluster_labels()
    api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))

    statefulset_labels=ot.get_statefulset_labels(api,args.namespace)
    statefulset_overscaler=statefulset_labels.loc[statefulset_labels['overscaler'] =="true"].reset_index()
    statefulset_overscaler=statefulset_overscaler.loc[:,['name','overscaler','current-count','autoscaler-count','max-replicas','min-replicas', 'metrics','rules']]

    current_nodes=ot.get_num_nodes()

    op.print_cluster_info(autoscale, max_nodes,min_nodes,overscaler,metrics,rules,current_nodes)
    op.print_statefulset_info(statefulset_labels)

    t_nodes=datetime.datetime.now()
    t_statefulset=datetime.datetime.now()
    while(True):

        t1=datetime.datetime.now()
        if (t1-t_nodes).seconds>int(args.refresh_cluster):
            ot.cluster_auth(args.zone, args.project)
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))
            autoscale, max_nodes, min_nodes, overscaler, metrics, rules = ot.get_cluster_labels()
            current_nodes = ot.get_num_nodes()
            op.print_cluster_info(autoscale, max_nodes, min_nodes, overscaler, metrics, rules, current_nodes)
            t_nodes = datetime.datetime.now()

        t2=datetime.datetime.now()
        if (t2-t_statefulset).seconds>int(args.refresh_statefulset):
            statefulset_labels = ot.get_statefulset_labels(api, args.namespace)
            op.print_statefulset_info(statefulset_labels)
            t_statefulset = datetime.datetime.now()

        df_node_status = ot.get_nodes_status(metrics,standard_node_metrics)
        op.print_node_status(df_node_status)

        for i in range(len(df_node_status['name'])):
            if overscaler=="true":
                ot.actions(df_node_status.loc[i,'status'], rules,df_node_status.loc[i,'name'],"NODE")


        df_pod_status=ot.get_pods_status(df_node_status.loc[i,'memory-allocatable'],df_node_status.loc[i,'cpu-allocatable'],statefulset_labels,standard_pod_metrics,args.namespace,api)
        if df_pod_status.empty:
            print(strftime("%Y-%m-%d %H:%M:%S", gmtime())+" [WARNING] Node "+str(df_node_status['name'][i])+" without pods to monitor")
        else:
            df_pod_status=df_pod_status.reset_index()
            op.print_pods_status(df_pod_status)
            for j in range(len(df_pod_status['pod'])):
                if not statefulset_overscaler.loc[statefulset_overscaler['name'] == str(df_pod_status.loc[j,'pod']).rsplit("-",1)[0]].empty:
                    ot.actions(api,df_pod_status.loc[j, 'status'], statefulset_overscaler.loc[statefulset_overscaler['name'] == str(df_pod_status.loc[j,'pod']).rsplit("-",1)[0]].reset_index().loc[0,"rules"], df_pod_status.loc[j, 'pod'],"POD",args.namespace,max_nodes)


        if not df_pod_status.empty:
            ot.upgrade_current_count(api, statefulset_overscaler['name'],args.namespace)

if __name__ == '__main__':
    main()






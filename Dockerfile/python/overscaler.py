import pykube
import overtools as ot
import overprint as op
import datetime




def main():

    # Parsing of arguments.
    args=ot.get_args()

    #Authentication in gcloud and kubernetes Api.
    ot.cluster_auth(args.zone,args.project)
    api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))

    #Starting kubernetes proxy.
    ot.start_proxy()

    #Getting information about cluster and stateful sets.
    autoscale, max_nodes,min_nodes,overscaler,metrics,rules = ot.get_cluster_labels(args.zone,args.project)
    statefulset_labels=ot.get_statefulset_labels(api,args.namespace)
    current_nodes=ot.get_num_nodes()

    #Printing information by console.
    op.print_cluster_info(autoscale,current_nodes, max_nodes,min_nodes,overscaler,metrics,rules)
    op.print_statefulset_info(statefulset_labels)

    #Counters for refreshing.
    t_nodes=datetime.datetime.now()
    t_statefulset=datetime.datetime.now()
    t_auth=datetime.datetime.now()

    while(True):

        #Is it necessary to refresh credentials?
        t1=datetime.datetime.now()
        if (t1-t_auth).seconds>int(args.refresh_auth):
            ot.cluster_auth(args.zone, args.project)
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))
            t_auth = datetime.datetime.now()

        #Is it necessary to refresh node information?
        t2=datetime.datetime.now()
        if (t2-t_nodes).seconds>int(args.refresh_cluster):
            autoscale, max_nodes, min_nodes, overscaler, metrics, rules = ot.get_cluster_labels(args.zone,args.project)
            current_nodes = ot.get_num_nodes()
            op.print_cluster_info(autoscale, current_nodes, max_nodes, min_nodes, overscaler, metrics, rules)
            t_nodes = datetime.datetime.now()

        #Is it necessary to refresh stateful set information?
        t3=datetime.datetime.now()
        if (t3-t_statefulset).seconds>int(args.refresh_statefulset):
            statefulset_labels = ot.get_statefulset_labels(api, args.namespace)
            op.print_statefulset_info(statefulset_labels)
            t_statefulset = datetime.datetime.now()


        #Getting node status and printing it.
        node_status = ot.get_node_status(metrics)
        op.print_node_status(node_status)

        #Getting pod status, printing and making decisions.
        pod_status=ot.get_pod_status(api,args.namespace,statefulset_labels,node_status[list(node_status.keys())[0]]['memory-allocatable'],node_status[list(node_status.keys())[0]]['cpu-allocatable'])
        if len(list(pod_status.keys())) > 0:
            op.print_pod_status(pod_status)
            ot.actions(api,args.namespace, pod_status, statefulset_labels, max_nodes)

            #Updating "current-count" label for all stateful set
            ot.update_current_count(api,args.namespace, statefulset_labels)

if __name__ == '__main__':
    main()






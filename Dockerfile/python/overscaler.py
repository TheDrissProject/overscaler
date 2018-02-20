import pykube
import overtools as ot
import overprint as op
import datetime
import subprocess
import json




def main():

    # Parsing of arguments.
    args=ot.get_args()

    #Authentication in gcloud and kubernetes Api.
    api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))

    #Starting kubernetes proxy.
    ot.start_proxy()

    #Getting information about cluster.

    bash_describe = "gcloud container clusters describe --format=json "+str(args.cluster)+" --zone "+str(args.zone)+" --project "+str(args.project)
    cluster_info = str(subprocess.check_output(bash_describe, shell=True)).replace("\\n", "").replace("b\'", "").replace("\'", "")
    cluster_info = json.loads(cluster_info)
    autoscale, max_nodes,min_nodes,metrics = ot.get_cluster_labels(cluster_info)
    current_nodes=ot.get_num_nodes()
    if autoscale==False: max_nodes, min_nodes =current_nodes, current_nodes

    #Getting information about Stateful Sets.
    statefulset_info = pykube.StatefulSet.objects(api).filter(namespace=args.namespace).response
    statefulset_labels=ot.get_statefulset_labels(statefulset_info)


    #Printing information by console.
    op.print_cluster_info(autoscale,current_nodes, max_nodes,min_nodes,metrics)
    op.print_statefulset_info(statefulset_labels)

    #Counters for refreshing.
    t_nodes=datetime.datetime.now()
    t_statefulset=datetime.datetime.now()
    t_auth=datetime.datetime.now()

    while(True):

        #Is it necessary to refresh credentials?
        t1=datetime.datetime.now()
        if (t1-t_auth).seconds>int(args.refresh_auth):
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))
            ot.start_proxy()
            t_auth = datetime.datetime.now()

        #Is it necessary to refresh node information?
        t2=datetime.datetime.now()
        if (t2-t_nodes).seconds>int(args.refresh_cluster):
            output = str(subprocess.check_output(bash_describe, shell=True)).replace("\\n", "").replace("b\'",
                                                                                                        "").replace(
                "\'", "")
            output = json.loads(output)
            autoscale, max_nodes, min_nodes, metrics= ot.get_cluster_labels(output)
            current_nodes = ot.get_num_nodes()
            if autoscale == False: max_nodes, min_nodes =current_nodes, current_nodes
            op.print_cluster_info(autoscale, current_nodes, max_nodes, min_nodes, metrics)
            t_nodes = datetime.datetime.now()

        #Is it necessary to refresh stateful set information?
        t3=datetime.datetime.now()
        if (t3-t_statefulset).seconds>int(args.refresh_statefulset):
            statefulset_info = pykube.StatefulSet.objects(api).filter(namespace=args.namespace).response
            statefulset_labels = ot.get_statefulset_labels(statefulset_info)
            op.print_statefulset_info(statefulset_labels)
            t_statefulset = datetime.datetime.now()


        #Getting node status and printing it.
        node_status, max_node_cpu, max_node_memory = ot.get_node_status(metrics)
        op.print_node_status(node_status)

        #Getting pod status, printing and making decisions.
        if node_status:
            pod_status=ot.get_pod_status(api,args.namespace,statefulset_labels,max_node_memory,max_node_cpu)
            if pod_status:
                op.print_pod_status(pod_status)
                ot.actions(api,args.namespace, pod_status, statefulset_labels, max_nodes)

                #Updating "current-count" label for all stateful set
                ot.update_current_count(api,args.namespace, statefulset_labels)

if __name__ == '__main__':
    main()






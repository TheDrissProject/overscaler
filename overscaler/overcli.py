import pykube
import datetime
import subprocess
import json
import click

from .overtools import (
    start_proxy,
    get_num_nodes,
    get_cluster_labels,
    get_statefulset_labels,
    get_node_status,
    get_pod_status,
    actions,
    update_current_count
    )

from .overprint import (
    print_cluster_info,
    print_statefulset_info,
    print_node_status,
    print_pod_status
)


@click.group(invoke_without_command=True)
@click.version_option()
@click.help_option()
def main():
    """Overscaler, Stateful Set autoscaling at Google Kubernetes Engine."""
    ctx = click.get_current_context()
    if ctx.invoked_subcommand is None:
        click.echo(main.get_help(ctx))
        click.echo("\nFor more information run: ")
        click.echo("overscaler COMMAND --help\n")



@main.command()
@click.option('--project','-pr', help="Project name.", required=True, type=click.STRING)
@click.option('--cluster','-c', help="Cluster name.", required=True, type=click.STRING)
@click.option('--zone','-z', help="Project zone name", required=True, type=click.STRING)
@click.option('--namespace','-n', help="Cluster namespace, default to \"default\".", type=click.STRING, default="default")
@click.option('--refresh_cluster', help="Refresh period for cluster labels (seconds). \n Default to 600.", type=click.INT, default=600)
@click.option('--refresh_statefulset', help="Refresh period for stateful set labels (seconds). \n Default to 300. (seconds).", type=click.INT, default=300)
@click.option('--refresh_auth', help="Refresh period for Api authentication (seconds). \n Default to 300. (seconds).", type=click.INT, default=300)
def start(cluster,namespace,project,zone,refresh_cluster,refresh_statefulset,refresh_auth):
    """Start Overscaler to monitor and autoscale.
    \n
    Monitoring and autoscaling are based on labels. Each Stateful Set must include a series of labels that define:
    \t\t\t\t\t\t\t
    - Overscaler is On or Off for this Stateful Set.
    \t\t\t\t\t\t\t
    - Metrics that will be monitored.
    \t\t\t\t\t\t\t
    - Rules that will be applied to rescale.

    """

    #gcloud command to get cluster info.
    bash_describe = "gcloud container clusters describe --format=json "+cluster+" --zone "+zone+" --project "+project


    #Counters for refreshing.
    t_cluster=0
    t_statefulset=0
    t_auth=0

    while(True):

        #Is it necessary to refresh credentials?
        t1=datetime.datetime.now()
        if t_auth==0 or (t1-t_auth).seconds>refresh_auth:
            # Authentication in gcloud and kubernetes Api.
            api = pykube.HTTPClient(pykube.KubeConfig.from_file("~/.kube/config"))
            # Starting kubernetes proxy.
            start_proxy()
            t_auth = datetime.datetime.now()

        #Is it necessary to refresh node information?
        t2=datetime.datetime.now()
        if t_cluster==0 or (t2-t_cluster).seconds>refresh_cluster:
            # Getting information about cluster.
            cluster_info = str(subprocess.check_output(bash_describe, shell=True)).replace("\\n", "").replace("b\'",
                                                                                                        "").replace(
                "\'", "")
            autoscale, max_nodes, min_nodes, metrics= get_cluster_labels(json.loads(cluster_info))
            current_nodes = get_num_nodes()
            if autoscale == False: max_nodes, min_nodes =current_nodes, current_nodes

            # Printing information by console.
            print_cluster_info(autoscale, current_nodes, max_nodes, min_nodes, metrics)
            t_cluster = datetime.datetime.now()

        #Is it necessary to refresh stateful set information?
        t3=datetime.datetime.now()
        if t_statefulset==0 or (t3-t_statefulset).seconds>refresh_statefulset:
            statefulset_info = pykube.StatefulSet.objects(api).filter(namespace=namespace).response
            statefulset_labels = get_statefulset_labels(statefulset_info)

            # Printing information by console.
            print_statefulset_info(statefulset_labels)
            t_statefulset = datetime.datetime.now()


        #Getting node status and printing it.
        node_status, max_node_cpu, max_node_memory = get_node_status(metrics)
        print_node_status(node_status)

        #Getting pod status, printing and making decisions.
        if node_status:
            pod_status=get_pod_status(api,namespace,statefulset_labels,max_node_memory,max_node_cpu)
            if pod_status:
                print_pod_status(pod_status)
                actions(api,namespace, pod_status, statefulset_labels, max_nodes)

                #Updating "current-count" label for all stateful set
                update_current_count(api,namespace, statefulset_labels)







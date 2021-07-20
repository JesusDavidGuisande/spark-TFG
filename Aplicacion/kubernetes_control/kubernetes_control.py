from kubernetes import *


class kubernetes_control:

    def __init__(self, namespace):
        self.namespace = namespace
        """
        self.utils = kubernetes.utils
        self.watch = kubernetes.watch
        self.dynamic = kubernetes.dynamic
        self.leaderelection = kubernetes.leaderelection
        self.stream = kubernetes.stream
        """
    def master_ip(self):
        # Configs can be set in Configuration class directly or using helper utility
        config.load_kube_config()
        v1 = client.CoreV1Api()
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            if 'kube-scheduler' in str(i.metadata.name):
                return i.status.pod_ip

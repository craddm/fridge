from pulumi import ComponentResource, ResourceOptions
from pulumi_kubernetes.helm.v3 import Release
from pulumi_kubernetes.yaml import ConfigFile

from enums import K8sEnvironment


class Ingress(ComponentResource):
    def __init__(
        self,
        name: str,
        k8s_environment: K8sEnvironment,
        opts: ResourceOptions | None = None,
    ) -> None:
        super().__init__("fridge:k8s:Ingress", name, {}, opts)
        child_opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))

        match k8s_environment:
            case K8sEnvironment.AKS:
                ingress_nginx = ConfigFile(
                    "ingress-nginx",
                    file="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.13.0/deploy/static/provider/cloud/deploy.yaml",
                    opts=child_opts,
                )
            case K8sEnvironment.DAWN:
                ingress_nginx = Release.get("ingress-nginx", "ingress-nginx")
            case K8sEnvironment.LOCAL:
                ingress_nginx = ConfigFile(
                    "ingress-nginx",
                    file="https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.13.0/deploy/static/provider/baremetal/deploy.yaml",
                    opts=child_opts,
                )

        self.ingress_nginx = ingress_nginx

import pulumi
from pulumi import ComponentResource, ResourceOptions
from pulumi_kubernetes.core.v1 import (
    Namespace,
)
from pulumi_kubernetes.helm.v3 import Release, RepositoryOptsArgs


class PolicyAgentArgs:
    def __init__(
        self,
        config: pulumi.config.Config,
    ) -> None:
        self.config = config


class PolicyAgent(ComponentResource):
    def __init__(
        self,
        name: str,
        args: PolicyAgentArgs,
        opts: ResourceOptions | None = None,
    ):
        super().__init__("fridge:k8s:PolicyAgent", name, {}, opts)
        child_opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))

        self.policy_agent_ns = Namespace(
            "policy-agent-ns",
            metadata={
                "name": "kyverno",
            },
            opts=child_opts,
        )

        self.policy_agent = Release(
            "kyverno",
            namespace=self.policy_agent_ns.metadata["name"],
            chart="kyverno",
            version="3.6.0",
            repository_opts=RepositoryOptsArgs(
                repo="https://kyverno.github.io/kyverno/",
            ),
            values={
                "admissionController.replicas": 1,
                "backgroundController.replicas": 1,
                "cleanupController.replicas": 1,
                "reportsController.replicas": 1,
                "webhook": {
                    "failurePolicy": "Fail",
                },
            },
            opts=child_opts,
        )

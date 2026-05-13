import pulumi
from pulumi import ComponentResource, ResourceOptions

from pulumi_azure_native import authorization, managedidentity


class IdentityArgs:
    def __init__(
        self,
        name: str,
        azure_config: pulumi.config.Config,
        disk_encryption_set_id: str,
        networking: ComponentResource,
        resource_group_name: str,
    ) -> None:

        self.name = name
        self.azure_config = azure_config
        self.disk_encryption_set_id = disk_encryption_set_id
        self.resource_group_name = resource_group_name
        self.networking = networking


class Identity(ComponentResource):
    def __init__(
        self, name: str, args: IdentityArgs, opts: ResourceOptions | None = None
    ):
        super().__init__("fridge_aks_cc:Identity", name, {}, opts)
        child_opts = ResourceOptions.merge(opts, ResourceOptions(parent=self))

        self.identity = managedidentity.UserAssignedIdentity(
            "cluster_managed_identity",
            resource_group_name=args.resource_group_name,
            opts=child_opts,
        )

        self.name = self.identity.name
        self.client_id = self.identity.client_id
        self.principal_id = self.identity.principal_id

        authorization.RoleAssignment(
            "cluster_role_assignment_disk_encryption_set",
            principal_id=self.identity.principal_id,
            principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
            # Contributor: https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
            role_definition_id=f"/subscriptions/{args.azure_config.require('subscriptionId')}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
            # The docs suggest using the scope of the resource group where the disk encryption
            # set is located. However, the scope of the disk encryption set seems sufficient.
            # Disks are created in the AKS managed resource group
            # https://learn.microsoft.com/en-us/azure/aks/azure-disk-customer-managed-keys#encrypt-your-aks-cluster-data-disk
            # scope=f"/subscriptions/{azure_config.require('subscriptionId')}"
            scope=args.disk_encryption_set_id,
        )

        # Grant the managed identity Contributor role on the access vnet so it can manage network interfaces
        # This allows the creation of internal load balancers to make it easier to direct traffic between the subnets
        authorization.RoleAssignment(
            "cluster_role_assignment_access_vnet",
            principal_id=self.identity.principal_id,
            principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
            # Contributor: https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
            role_definition_id=f"/subscriptions/{args.azure_config.require('subscriptionId')}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
            scope=args.networking.access_nodes.id,
        )

        # Grant the managed identity Contributor role on the isolated vnet so it can manage network interfaces
        # This allows the creation of internal load balancers to make it easier to direct traffic to the right place on the isolated network
        authorization.RoleAssignment(
            "cluster_role_assignment_isolated_vnet",
            principal_id=self.identity.principal_id,
            principal_type=authorization.PrincipalType.SERVICE_PRINCIPAL,
            # Contributor: https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
            role_definition_id=f"/subscriptions/{args.azure_config.require('subscriptionId')}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c",
            scope=args.networking.isolated_nodes.id,
        )

        self.register_outputs({"identity": self.identity})

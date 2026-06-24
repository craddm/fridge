import base64

import components
import pulumi
import pulumi_random as random
import pulumi_tls as tls
from pulumi_azure_native import (
    compute,
    containerservice,
    keyvault,
    managedidentity,
    resources,
)


def get_kubeconfig(
    credentials: list[containerservice.outputs.CredentialResultResponse],
) -> str | None:
    for credential in credentials:
        if credential.name == "clusterAdmin":
            return base64.b64decode(credential.value).decode()


config = pulumi.Config()
azure_config = pulumi.Config("azure-native")

resource_group = resources.ResourceGroup(
    "resource_group",
    resource_group_name=config.require("resource_group_name"),
)

ssh_key = tls.PrivateKey("ssh-key", algorithm="RSA", rsa_bits="3072")

suffix = random.RandomString(
    "suffix", length=8, lower=True, numeric=True, special=False
)

kv = keyvault.Vault(
    "keyvault",
    vault_name=pulumi.Output.concat("fridge-kv-", suffix.result),
    properties=keyvault.VaultPropertiesArgs(
        # To use this keyvault for BYOK, it requires vault authorisation (not RBAC),
        # purge protection and soft delete
        enable_purge_protection=True,
        enable_rbac_authorization=False,
        enable_soft_delete=True,
        sku=keyvault.SkuArgs(
            family=keyvault.SkuFamily.A,
            name=keyvault.SkuName.STANDARD,
        ),
        soft_delete_retention_in_days=90,
        tenant_id=azure_config.require("tenantId"),
    ),
    resource_group_name=resource_group.name,
)

disk_encryption_key = keyvault.Key(
    "disk-encryption-key",
    key_name="fridge-pvc-key",
    resource_group_name=resource_group.name,
    vault_name=kv.name,
    properties=keyvault.KeyPropertiesArgs(
        key_size=2048,
        kty=keyvault.JsonWebKeyType.RSA,
    ),
)

disk_encryption_set = compute.DiskEncryptionSet(
    "disk-encryption-set",
    resource_group_name=resource_group.name,
    disk_encryption_set_name="fridge-disk-encryption-set",
    active_key=compute.KeyForDiskEncryptionSetArgs(
        key_url=disk_encryption_key.key_uri_with_version,
    ),
    encryption_type=compute.DiskEncryptionSetType.ENCRYPTION_AT_REST_WITH_CUSTOMER_KEY,
    identity=compute.EncryptionSetIdentityArgs(
        type=compute.DiskEncryptionSetIdentityType.SYSTEM_ASSIGNED,
    ),
)

# Grant disk encryption set permission to use keyvault keys
access_policy = keyvault.AccessPolicy(
    "access-policy",
    vault_name=kv.name,
    resource_group_name=resource_group.name,
    policy=keyvault.AccessPolicyEntryArgs(
        object_id=disk_encryption_set.identity.principal_id,
        tenant_id=azure_config.require("tenantId"),
        permissions=keyvault.PermissionsArgs(
            keys=[
                keyvault.KeyPermissions.UNWRAP_KEY,
                keyvault.KeyPermissions.WRAP_KEY,
                keyvault.KeyPermissions.GET,
            ],
        ),
    ),
)

# Networking
networking = components.Networking(
    "networking",
    components.NetworkingArgs(
        config=config,
        resource_group_name=resource_group.name,
        location=resource_group.location,
    ),
)

# Managed identity for the k8s clusters

identity = components.Identity(
    "cluster_managed_identity",
    components.IdentityArgs(
        name="cluster_managed_identity",
        azure_config=azure_config,
        disk_encryption_set_id=disk_encryption_set.id,
        networking=networking,
        resource_group_name=resource_group.name,
    ),
)

# Create access cluster

# This is a public facing cluster that will run proxies to the private cluster

access_cluster = components.AccessCluster(
    "access-cluster",
    components.AccessClusterArgs(
        config=config,
        resource_group_name=resource_group.name,
        cluster_name=f"{config.require('cluster_name')}-access",
        identity=identity,
        nodes_subnet_id=networking.access_nodes_subnet_id,
        ssh_key=ssh_key,
    ),
)

access_admin_credentials = (
    containerservice.list_managed_cluster_admin_credentials_output(
        resource_group_name=resource_group.name, resource_name=access_cluster.name
    )
)

# Create isolated cluster to host private workloads
isolated_cluster = components.IsolatedCluster(
    "isolated-cluster",
    components.IsolatedClusterArgs(
        config=config,
        disk_encryption_set=disk_encryption_set,
        resource_group_name=resource_group.name,
        cluster_name=f"{config.require('cluster_name')}-isolated",
        identity=identity,
        nodes_subnet_id=networking.isolated_nodes_subnet_id,
        ssh_key=ssh_key,
    ),
)

isolated_admin_credentials = (
    containerservice.list_managed_cluster_admin_credentials_output(
        resource_group_name=resource_group.name, resource_name=isolated_cluster.name
    )
)

# Create federated identity credential for workload identity
#
# This cannot be created until the isolated cluster is created, because it needs the OIDC issuer URL from the cluster

federated_identity_credential = managedidentity.FederatedIdentityCredential(
    "federated-identity-credential",
    name="fridge-federated-identity-credential",
    federated_identity_credential_name="fridge-federated-identity-credential",
    resource_group_name=resource_group.name,
    audiences=["api://AzureADTokenExchange"],
    issuer=isolated_cluster.odic_issuer_url,
    subject="system:serviceaccount:confidential-containers-system:cloud-api-adaptor",
)

access_kubeconfig = access_admin_credentials.kubeconfigs.apply(get_kubeconfig)
isolated_kubeconfig = isolated_admin_credentials.kubeconfigs.apply(get_kubeconfig)

pulumi.export("access_kubeconfig", access_kubeconfig)
pulumi.export("isolated_kubeconfig", isolated_kubeconfig)
pulumi.export("oidc_issuer_url", isolated_cluster.odic_issuer_url)

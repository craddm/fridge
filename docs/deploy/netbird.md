# Connecting to FRIDGE using NetBird

You will require access to a NetBird Management server.
For testing and development, the free NetBird cloud management server is sufficient.
However, for production, we recommend using [self-hosted NetBird](https://docs.netbird.io/selfhosted/selfhosted-quickstart).

## Configuring NetBird

Once you have access to a NetBird management server, you are ready to begin setting up your mesh VPN network.

FRIDGE will deploy with a NetBird agent present in the access cluster.
You need to make the agent become a `peer` on the mesh network.
You will need to provide a [setup key](https://docs.netbird.io/manage/peers/register-machines-using-setup-keys) at the time of deployment to automatically connect the agent to your mesh network.
Before creating the setup key, we recommend first setting up the configuration of your mesh network.

The FRIDGE deployment controls the movement of traffic within the FRIDGE itself, but you will also need to configure [network access within NetBird](https://docs.netbird.io/manage/access-control/manage-network-access).
We make use of Groups and Access Policies.
Individual NetBird peers can be associated with Groups.
A peer is allowed to access any other resource in Groups it is associated with.

Access Policies can be used to determine which Groups of peers can connect to each other, as well as in which directions and on what ports.

We recommend creating three Groups, into which you will place one or more peers:
1. A Group for the NetBird peer in the access cluster (e.g. `fridge-access`)
2. A Group for TRE Operator administrator devices (e.g. `tre-admin`)
3. A Group for TRE User access (e.g. `tre-user`)

Peers can be manually placed in these groups after creation.
It is also possible to create setup keys that automatically place peers in groups.

Any TRE Operator administrator devices that are intended to be used for communication with the Kubernetes API of the isolated cluster should be allocated to the `tre-admin` group.

You can then create Access policies that allow traffic to flow between each of these groups in specific ways.
In the NetBird management console, create an access policy that allows traffic to flow from the `tre-users` group to `fridge-access` on port 8000.
Then create an access policy that allows traffic to flow from the `tre-admins` group to `fridge-access` on port 6443.
This setup is shown in [](#netbird-access-policies).

```{figure} ../static/NetBird_access_policies.png
---
name: netbird-access-policies
alt: An example of the correct setup for NetBird Access policies.
---
```

Inside the access cluster, traffic over NetBird is routed to its destination in the isolated cluster using HAProxy.
Traffic on port 6443 will be routed to the Kubernetes API of the isolated cluster.
Traffic on port 8000 will be routed to the FRIDGE API.

## Connecting over the VPN

To connect to the FRIDGE over the VPN, you can use either the IP address or FQDN of the NetBird peer inside the FRIDGE from another registered peer.
For example, if you are connecting as a TRE Admin to the internal K8s API of the isolated cluster, you can connect using

```console
https://<access-peer-netbird-ip>:6443
```

or

```console
https://<access-peer-netbird-FQDN>:6443
```

## Pulumi stack configuration

```yaml
config:
  fridge-access:netbird:
    hostname: <stable-name-for-the-access-peer>
    management_url:
      secure: <NetBird-management-URL>
      secret: true
    setup_key:
      secure: <NetBird-setup-key>
      secret: true
```

`hostname` should be a stable, descriptive name for the peer in the access cluster (e.g. `fridge-access-prod`).

We recommend using a single-use NetBird setup key.
The peer will store its credentials in the cluster in a way that will survive pod restarts, so it is not necessary to make the key reusable.

At present, only Netbird Cloud is fully supported.
`management_url` is the FQDN for NetBird's API server.
The `management_url` defaults to that of the Netbird Cloud api.

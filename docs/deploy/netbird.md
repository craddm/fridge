# Connecting to FRIDGE using NetBird

You will require access to a NetBird Management server.
For testing and development, the free NetBird cloud management server is sufficient.
However, for production, we recommend using [self-hosted NetBird](https://docs.netbird.io/selfhosted/selfhosted-quickstart).

## Configuring NetBird

Once you have access to a NetBird management server, you are ready to begin setting up your mesh VPN network.

The FRIDGE deployment controls the movement of traffic within the FRIDGE itself, but you will also need to configure [network access within NetBird](https://docs.netbird.io/manage/access-control/manage-network-access).
FRIDGE will deploy with a NetBird agent present in the access cluster.
You need to make the agent become a `peer` on the mesh network.
You will need to provide a [setup key](https://docs.netbird.io/manage/peers/register-machines-using-setup-keys) at the time of deployment to automatically connect the agent to your mesh network.
Any device that will connect directly to the VPN network will need to become a peer on that network.
Use setup keys for this purpose.

We make use of [Groups](https://docs.netbird.io/manage/access-control/manage-network-access#groups) and [Access Policies](https://docs.netbird.io/manage/access-control/manage-network-access#creating-policies) to control who can access which parts of the FRIDGE over the VPN.

Individual NetBird peers can be associated with Groups.
A peer is allowed to access any other resource in Groups it is associated with.

Access Policies can be used to determine which Groups can connect to each other, in which directions traffic can flow and on what ports and protocols.

We recommend creating three Groups, into each of which you will place one or more peers:
1. A Group for the NetBird peer in the access cluster (e.g. `fridge-access`)
2. A Group for TRE Operator administrator devices (e.g. `tre-admins`)
3. A Group for TRE User access (e.g. `tre-users`)

Peers can be manually allocated to these groups after creation, or automatically allocated using setup keys.

Any `TRE Operator` administrator devices that are intended to be used for communication with the Kubernetes API of the isolated cluster should be allocated to the `tre-admins` Group.

Any device through which `TRE Users` connect to the FRIDGE API should be allocated to the `tre-users` Group.

Inside the access cluster, traffic over NetBird is routed to its destination in the isolated cluster using HAProxy.
Traffic on port 6443 will be routed to the Kubernetes API of the isolated cluster.
Traffic on port 8000 will be routed to the FRIDGE API.

In the NetBird management console, create an access policy that allows traffic to flow from the `tre-users` group to `fridge-access` on port 8000.
Then create an access policy that allows traffic to flow from the `tre-admins` group to `fridge-access` on port 6443.
This setup is shown in [](#netbird-access-policies).

```{figure} ../static/NetBird_access_policies.png
---
name: netbird-access-policies
alt: An example of the correct setup for NetBird Access policies.
---
```


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

When intending to use the Kubernetes API through the VPN, you will need to modify your Kubernetes context.
We recommend using a copy of your original context.
Modify the `server` field to match either the NetBird IP address or FQDN, as appropriate.
Modify or add the `tls-server-name:` with the value `localhost` on Dawn, or the private Azure API FQDN when using AKS.

## Pulumi stack configuration

Additional NetBird-specific configuration fields are required in the Pulumi configuration.
If using NetBird Cloud, most of these fields have appropriate default values.
If using self-hosted NetBird, you will need to provide values pointing to your self-hosted instance.

```yaml
config:
  fridge-access:netbird:
    hostname: <stable-name-for-the-access-peer>
    management_url:
      value: "https://api.netbird.io:443"
      secure: <NetBird-management-URL>
      secret: true
    setup_key:
      secure: <NetBird-setup-key>
      secret: true
```

`hostname` should be a stable, descriptive name for the peer in the access cluster (e.g. `fridge-access-prod`).

We recommend using a single-use NetBird setup key.
The peer will store its credentials in the cluster in a way that will survive pod restarts, so it is not necessary to make the key reusable.

At present, only NetBird Cloud is supported.
`management_url` is the FQDN for NetBird's API server.
The `management_url` defaults to that of the NetBird Cloud api.

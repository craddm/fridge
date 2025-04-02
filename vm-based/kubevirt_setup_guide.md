## Set up Kubevirt

The first step is to install the `kubevirt-operator`, which manages all the Kubevirt resources that are deployed in the second step.

At the time of writing, the latest version is `v1.4.0`.

```bash
kubectl create -f "https://github.com/kubevirt/kubevirt/releases/download/v1.4.0/kubevirt-operator.yaml"
```

The second step adds custom resources.
This is the step that actually deploys the Kubevirt resources.
An issue for deploying on AKS is that the installation script is looking for nodes with the `control-plane` role, but AKS does not expose the control plane to the user/customer.
The solution is either to label the nodes with the role or to modify the installation script.

A modified installation script is provided in the `kubevirt-customise-cr.yaml` file in this repository.
This script removes the requirement for Kubevirt infrastructure to be deployed on nodes with the `control-plane` role.
In a future iteration, we may want to add a separate node pool for Kubevirt resources and direct Kubevirt to deploy on that pool.

```bash
kubectl apply -f kv-customise-cr.yaml
```

Note that this file is also useful for enabling additional Kubevirt features such as snapshotting or live migration of VMs.
For now, we will leave the additional features disabled.

### Optional/advanced configuration steps

#### Using the default installation script for non-AKS clusters

As an alternative to the modified installation script, the default installation script can be used.

```bash
kubectl create -f "https://github.com/kubevirt/kubevirt/releases/download/v1.4.0/kubevirt-cr.yaml"
```

You can then apply the `control-plane` role to all nodes using `kubectl label nodes`:

```bash
kubectl label nodes --all 'node-role.kubernetes.io/control-plane=control-plane'
```

To be more specific, applying the control plane role only to the `system` node, use

```bash
kubectl label nodes -l 'kubernetes.azure.com/mode=system' 'node-role.kubernetes.io/control-plane=control-plane'
```

Note that by default Kubevirt will make it possible for VMs to be scheduled on all nodes (including system nodes).
This can be changed by modifying the `kubevirt-customise-cr.yaml` file.
The field `workloads` can be added to the `spec` section of the `Kubevirt` resource, with the subfield `nodePlacement` to specify which nodes VMs can be scheduled on.

See <https://kubevirt.io/user-guide/cluster_admin/installation/#restricting-kubevirt-components-node-placement> for more information.

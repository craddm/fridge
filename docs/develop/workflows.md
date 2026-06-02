# Argo Workflows

This guide contains guidance for the creation of Argo Workflows `Workflows` and `WorkflowTemplates` within FRIDGE.

For more general guidance on how to create workflows, see the official [Argo Workflows user guide](https://argo-workflows.readthedocs.io/en/latest/workflow-concepts/)

## FRIDGE Workflow requirements

Workflows in FRIDGE run in the `argo-workflows` namespace.
The namespace Pod Security Standards set to [`RESTRICTED`](https://kubernetes.io/docs/concepts/security/pod-security-standards/#restricted).

This means that all Workflows must create non-root, unprivileged containers.
Note that these fields do not need to be explicitly set.
By default, Argo Workflows in FRIDGE has been configured to run pods with the following security context, which meets `restricted` standards:

```yaml
securityContext:
    allowPrivilegeEscalation: false
    capabilities:
      drop:
        - ALL
    runAsGroup: 8737
    runAsNonRoot: true
    runAsUser: 8737
    seccompProfile:
      type: RuntimeDefault
```

If you modify any of these fields in your Workflow or Workflow template, the pod will be rejected and your workflow will fail to run.

## Creating and Deploying a Workflow Template

Workflows and WorkflowTemplates are defined using YAML.

There are several ways that `WorkflowTemplates` can be deployed.

1. Create the `WorkflowTemplate` using `kubectl apply -f your_template.yaml -n argo-workflows`
2. Add the file defining the WorkflowTemplate to the custom directory, and deploy it using `pulumi up`
3. Create the `WorkflowTemplate` directly using the Argo Workflows GUI

## Enabling use of MinIO

Note that MinIO uses a self-signed TLS certificate to encrypt traffic within the cluster.
The relevant certificate is included in a certificate bundle in the `argo-workflows` namespace.
It is recommended to overwrite any SSL certificate bundle in the container as follows:

```yaml
    container:
        volumeMounts:
            - ssl-certs
              readOnly: True
                mountPath: /etc/ssl/certs
    volumes:
        - name: ssl-certs
          secret:
            secretName: trusted-certificates
```

## Enabling GPU access within a workflow

A workflow intended to run using a GPU must have several additional elements specified.

1. A supplemental group (`110`) to give the non-root container permission to use the GPU.
2. A resource request for the specific GPU family on the platform you are using.

```yaml
resources:
    limits:
        gpu.intel.com/i915: "1"
```

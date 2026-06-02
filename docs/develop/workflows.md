# Argo Workflows

This guide contains guidance for the creation of Argo Workflows `Workflows` and `WorkflowTemplates` within FRIDGE.

For more general guidance on how to create workflows, see the official [Argo Workflows user guide](https://argo-workflows.readthedocs.io/en/latest/workflow-concepts/)

## Creating and Deploying a Workflow Template

Workflows and WorkflowTemplates are defined using YAML.

There are several ways that `WorkflowTemplates` can be deployed.

1. Create the `WorkflowTemplate` using `kubectl apply -f your_template.yaml -n argo-workflows`
2. Add the file defining the WorkflowTemplate to the custom directory, and deploy it using `pulumi up`
3. Create the `WorkflowTemplate` directly using the Argo Workflows GUI

## Enabling use of MinIO

## Enabling GPU access within a workflow

A workflow intended to run using a GPU must have several additional elements specified.

1. A supplemental group (`110`) to give the non-root container permission to use the GPU.
2. A resource request for the specific GPU family on the platform you are using.

```yaml
resources:
    limits:
        gpu.intel.com/i915: "1"
```

# TES2ARGO

This module provides a translator that converts TES (Task Execution Service) task definitions into Argo Workflows templates. It allows users to run TES-defined tasks within an Argo Workflow environment.

## Usage

To use the TES2ARGO translator, you need to have a TES task definition in JSON format. The translator will convert this definition into an Argo Workflow template.

### Example TES Task Definition

```json
{
  "name": "example-task",
  "inputs": {
    "files": [
      {
        "path": "/data/input.txt",
        "uri": "s3://my-bucket/input.txt"
      }
    ]
  },
  "outputs": {
    "files": [
      {
        "path": "/data/output.txt",
        "uri": "s3://my-bucket/output.txt"
      }
    ]
  },
  "resources": {
    "cpu_cores": 2,
    "ram_gb": 4,
    "disk_gb": 10
  },
  "command": [
    "python",
    "/app/process.py",
    "/data/input.txt",
    "/data/output.txt"
  ]
}
```

### Translating to Argo Workflow

To translate the above TES task definition into an Argo Workflow template, you can use the TES2ARGO translator module. The resulting Argo Workflow template will look something like this:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: example-task-
spec:
  entrypoint: example-task
  templates:
  - name: example-task
    container:
      image: my-tes-image
      command: ["python", "/app/process.py", "/data/input.txt", "/data/output.txt"]
      resources:
        limits:
          cpu: "2"
          memory: "4Gi"
      volumeMounts:
      - name: data-volume
        mountPath: /data
    volumes:
    - name: data-volume
      persistentVolumeClaim:
        claimName: my-pvc
```

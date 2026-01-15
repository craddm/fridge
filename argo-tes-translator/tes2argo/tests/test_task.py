from src.main import parse_tes_task
from src.tes_models import TesTask

example_tes_task_json = """
{
    "name": "example_task",
    "description": "An example TES task",
    "tags": {"example": "test"},
    "inputs": [
        {
            "name": "input_file",
            "description": "An input file",
            "type": "FILE",
            "path": "/data/input.txt",
            "size": 1024
        }
    ],
    "outputs": [
        {
            "name": "output_file",
            "description": "An output file",
            "url": "http://example.com/output.txt",
            "path": "/data/output.txt"
        }
    ],
    "resources": {
        "cpu_cores": 2,
        "ram_gb": 4,
        "disk_gb": 10
    },
    "executors": [
        {
            "image": "python:3.8",
            "command": ["python", "script.py", "--input", "/data/input.txt", "--output", "/data/output.txt"]
        }
    ]
}
"""


def test_parse_tes_task():
    task = parse_tes_task(example_tes_task_json)

    assert isinstance(task, TesTask)

    assert task.name == "example_task"
    assert task.description == "An example TES task"
    assert task.tags == {"example": "test"}

    assert len(task.inputs) == 1
    assert task.inputs[0].name == "input_file"
    assert task.inputs[0].path == "/data/input.txt"

    assert len(task.outputs) == 1
    assert task.outputs[0].name == "output_file"
    assert task.outputs[0].path == "/data/output.txt"

    assert task.resources.cpu_cores == 2
    assert task.resources.ram_gb == 4
    # assert task_info["resources"]["disk_gb"] == 10

    assert len(task.executors) == 1
    assert task.executors[0].image == "python:3.8"
    assert task.executors[0].command == [
        "python",
        "script.py",
        "--input",
        "/data/input.txt",
        "--output",
        "/data/output.txt",
    ]

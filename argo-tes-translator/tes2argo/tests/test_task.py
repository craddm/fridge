import pytest
from src.main import parse_tes_task

example_tes_task_json = """
{
    "name": "example_task",
    "description": "An example TES task",
    "tags": ["example", "test"],
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
            "type": "FILE",
            "path": "/data/output.txt",
            "size": 2048
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
            "command": ["python", "script.py"],
            "args": ["--input", "/data/input.txt", "--output", "/data/output.txt"]
        }
    ]
}
"""


def test_parse_tes_task():
    task_info = parse_tes_task(example_tes_task_json)

    assert task_info["name"] == "example_task"
    assert task_info["description"] == "An example TES task"
    assert task_info["tags"] == ["example", "test"]

    assert len(task_info["inputs"]) == 1
    assert task_info["inputs"][0]["name"] == "input_file"
    assert task_info["inputs"][0]["path"] == "/data/input.txt"

    assert len(task_info["outputs"]) == 1
    assert task_info["outputs"][0]["name"] == "output_file"
    assert task_info["outputs"][0]["path"] == "/data/output.txt"

    assert task_info["resources"]["cpu_cores"] == 2
    assert task_info["resources"]["ram_gb"] == 4
    assert task_info["resources"]["disk_gb"] == 10

    assert len(task_info["executors"]) == 1
    assert task_info["executors"][0]["image"] == "python:3.8"
    assert task_info["executors"][0]["command"] == ["python", "script.py"]
    assert task_info["executors"][0]["args"] == [
        "--input",
        "/data/input.txt",
        "--output",
        "/data/output.txt",
    ]

import json

from pydantic import BaseModel


class TesTaskModel(BaseModel):
    name: str
    description: str = None
    tags: list = []
    inputs: list = []
    outputs: list = []
    resources: dict = {}
    executors: list = []


def parse_tes_task(tes_task_json):
    """
    Parses a TES task JSON and extracts relevant information.

    Args:
        tes_task_json (str): A JSON string representing the TES task.
    Returns:
        dict: A dictionary containing extracted information.
    """
    tes_task = json.loads(tes_task_json)

    task_info = {
        "name": tes_task.get("name"),
        "description": tes_task.get("description"),
        "tags": tes_task.get("tags", []),
        "inputs": tes_task.get("inputs", []),
        "outputs": tes_task.get("outputs", []),
        "resources": tes_task.get("resources", {}),
        "executors": tes_task.get("executors", []),
    }

    return task_info

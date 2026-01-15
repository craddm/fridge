import json

from .tes_models import TesExecutor, TesInput, TesOutput, TesResources, TesTask


def parse_tes_task(tes_task_json):
    """
    Parses a TES task JSON and extracts relevant information.

    Args:
        tes_task_json (str): A JSON string representing the TES task.
    Returns:
        dict: A dictionary containing extracted information.
    """
    tes_task = json.loads(tes_task_json)
    task_inputs = [TesInput(**x) for x in tes_task.get("inputs", [])]
    task_outputs = [TesOutput(**output) for output in tes_task.get("outputs", [])]
    task_resources = TesResources(**tes_task.get("resources", {}))
    task_executors = [
        TesExecutor(**executor) for executor in tes_task.get("executors", [])
    ]

    task = TesTask(
        name=tes_task.get("name"),
        description=tes_task.get("description"),
        tags=tes_task.get("tags", []),
        inputs=task_inputs,
        outputs=task_outputs,
        resources=task_resources,
        executors=task_executors,
    )

    return task

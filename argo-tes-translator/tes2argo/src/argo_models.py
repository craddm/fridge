from pydantic import BaseModel


class ArgoContainer(BaseModel):
    image: str
    command: list[str] = []
    args: list[str] = []


class ArgoScript(BaseModel):
    image: str
    command: list[str] = []
    source: str = ""


class ArgoTemplate(BaseModel):
    name: str
    container: ArgoContainer | None = None
    script: ArgoScript | None = None
    inputs: dict | None = None


class ArgoWorkflowSpec(BaseModel):
    name: str
    templates: list[ArgoTemplate]

from typing import TypedDict,Annotated


class AgentState(TypedDict):
    question:str
    route:str
    answer:str
# src/comm/__init__.py

from src.comm.communication import (
    Component,
    Model as BaseModel,
    port,
    inport,
    outport,
    Connector,
    Data_Transformation,
    Port,  # we’ll add this alias in communication.py
)

from src.comm.components import (
    Source,
    Sink,
    Model,  # full simulation model, overrides BaseModel
    Duplicator,
    Transformation,
    Aggregator,
    Splitter,
    Switch,
    ConfigComp,  # we’ll add this as an alias or class in components.py
)

__all__ = [
    # communication
    "Component",
    "BaseModel",
    "Model",  # this will be the full DT model from components.py
    "port",
    "Port",   # alias for port
    "inport",
    "outport",
    "Connector",
    "Data_Transformation",
    # components
    "Source",
    "Sink",
    "Duplicator",
    "Transformation",
    "Aggregator",
    "Splitter",
    "Switch",
    "ConfigComp",
]
# src/comm/components.py

"""
Concrete LOTTS digital twin components.

These classes inherit from the base abstractions in communication.py
and implement specific behavior for each component type.
"""

from typing import Any, Dict, List, Optional

from src.comm.communication import (
    Component,
    Model as BaseModel,
    port,
    inport,
    outport,
    Data_Transformation,
)


# -----------------------------------------------------------------------------
# Source / Sensor
# -----------------------------------------------------------------------------

class Source(Component):
    """
    Sensor / source component: produces outputs, no inputs.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        # Sources typically have no inputs
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Generate output values (e.g., from a sensor or data source).

        Concrete implementation depends on how your sources are defined.
        For now, this is a placeholder.
        """
        # Example:
        # for out in self.outputs:
        #     outputs[out.name] = some_sensor_value(time)
        raise NotImplementedError("Implement Source.behavior() for your use case")


# -----------------------------------------------------------------------------
# Sink / UX
# -----------------------------------------------------------------------------

class Sink(Component):
    """
    UX / sink component: consumes inputs, may produce no outputs (or status outputs).
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Consume input values (e.g., log, display, store).

        Concrete implementation depends on your sink logic.
        """
        # Example:
        # for inp_name, val in inputs.items():
        #     log_or_store(inp_name, val)
        raise NotImplementedError("Implement Sink.behavior() for your use case")


# -----------------------------------------------------------------------------
# Model (simulation model: FMU, Python, etc.)
# -----------------------------------------------------------------------------

class Model(BaseModel):
    """
    LOTTS-level model component, specializing the base Model.

    This is what LOTTS generates for:
      - Dataprocess → Python model
      - Model → FMU model
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        parameters: Optional[Dict[str, Any]] = None,
        sim_engine: str = "Python",  # "FMU" or "Python"
        model_dir: str = "",
        backend: Optional[Any] = None,
    ):
        super().__init__(name=name, inputs=inputs, outputs=outputs, parameters=parameters)
        self.sim_engine = sim_engine
        self.model_dir = model_dir
        self.backend = backend  # FMU or Wrapping instance

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Advance the underlying model (FMU or Python) by one step.

        Typical steps:
          - Set inputs into the backend
          - Call backend.advance(...)
          - Read outputs from backend and populate `outputs`
        """
        if self.backend is None:
            raise RuntimeError(f"Model {self.name!r} has no backend initialized")

        # Set inputs
        for name, val in inputs.items():
            self.backend.set_input(name, val)

        # Advance one step
        new_outputs = self.backend.advance()

        # Populate outputs dict
        for name, val in new_outputs.items():
            outputs[name] = val


# -----------------------------------------------------------------------------
# Duplicator
# -----------------------------------------------------------------------------

class Duplicator(Component):
    """
    Duplicator: one input, multiple identical outputs.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Copy the input value to all outputs.
        """
        if not self.inputs:
            return
        in_val = inputs.get(self.inputs[0].name, 0)
        for out in self.outputs:
            outputs[out.name] = in_val


# -----------------------------------------------------------------------------
# Transformation (LOTTS-level)
# -----------------------------------------------------------------------------

class Transformation(Component):
    """
    LOTTS-level transformation component: applies expressions to inputs to produce outputs.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        expressions: Optional[List[str]] = None,
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])
        self.expressions = expressions or []

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Apply transformation expressions to inputs to compute outputs.

        Concrete implementation depends on how you encode/evaluate expressions.
        """
        # Example pattern (pseudo-code):
        # env = dict(inputs)
        # for expr in self.expressions:
        #     out_name, value = eval_expression(expr, env)
        #     outputs[out_name] = value
        raise NotImplementedError("Implement Transformation.behavior() for your use case")


# -----------------------------------------------------------------------------
# Aggregator
# -----------------------------------------------------------------------------

class Aggregator(Component):
    """
    Aggregator: multiple inputs, one output (e.g., sum, average).
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        operation: str = "sum",
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])
        self.operation = operation

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Aggregate input values into a single output.
        """
        vals = list(inputs.values())
        if not vals:
            return
        if self.operation == "sum":
            out_val = sum(vals)
        elif self.operation == "avg":
            out_val = sum(vals) / len(vals)
        else:
            # Default to first input
            out_val = vals[0]

        if self.outputs:
            outputs[self.outputs[0].name] = out_val


# -----------------------------------------------------------------------------
# Splitter
# -----------------------------------------------------------------------------

class Splitter(Component):
    """
    Splitter: one input, multiple outputs (possibly with selection logic).
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Forward the input value to all outputs (or implement splitting logic).
        """
        if not self.inputs:
            return
        in_val = inputs.get(self.inputs[0].name, 0)
        for out in self.outputs:
            outputs[out.name] = in_val


# -----------------------------------------------------------------------------
# Switch
# -----------------------------------------------------------------------------

class Switch(Component):
    """
    Switch: multiple inputs, one output, selected by a condition.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        condition: str = "",
    ):
        super().__init__(name=name, inputs=inputs or [], outputs=outputs or [])
        self.condition = condition

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Select one input based on `condition` and forward to output.

        Concrete implementation depends on how you encode/evaluate the condition.
        """
        # Example pattern (pseudo-code):
        # selected_name = eval_condition(self.condition, inputs)
        # outputs[self.outputs[0].name] = inputs[selected_name]
        raise NotImplementedError("Implement Switch.behavior() for your use case")

# Backward-compatibility alias: ConfigComp is a Model with configuration support
ConfigComp = Model
# src/comm/communication.py

"""
Core communication and interoperability primitives for digital twin services.

This module defines:
  - Port abstractions (port, inport, outport)
  - Base component abstractions (Component, Operation, Transformation, Model)
  - Connection and data transformation abstractions (Connector, Data_Transformation, Ex_Pattern, OldEx_Pattern)
"""

from typing import Any, Dict, List, Optional


# -----------------------------------------------------------------------------
# Ports
# -----------------------------------------------------------------------------

class port:
    """
    Base port abstraction.
    Typically holds:
      - name
      - datatype / type
      - unit
      - current value
    """

    def __init__(
        self,
        name: str = "",
        typ: str = "float",
        unit: str = "",
        val: Any = None,
    ):
        self.name = name
        self.typ = typ
        self.unit = unit
        self.val = val

    def __repr__(self):
        return f"port(name={self.name!r}, typ={self.typ!r}, unit={self.unit!r}, val={self.val!r})"

# Alias for backward compatibility with existing code
Port = port

class inport(port):
    """
    Input port: receives data from other components.
    """

    def __init__(
        self,
        name: str = "",
        typ: str = "float",
        unit: str = "",
        val: Any = None,
    ):
        super().__init__(name=name, typ=typ, unit=unit, val=val)


class outport(port):
    """
    Output port: sends data to other components.
    """

    def __init__(
        self,
        name: str = "",
        typ: str = "float",
        unit: str = "",
        val: Any = None,
    ):
        super().__init__(name=name, typ=typ, unit=unit, val=val)


# -----------------------------------------------------------------------------
# Base component abstractions
# -----------------------------------------------------------------------------

class Component:
    """
    Base class for all digital twin components in the communication view.

    Common responsibilities:
      - Hold inputs and outputs (lists of ports)
      - Have a name / identifier
      - Define a `behavior` method used by the execution engine
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        self.name = name
        self.inputs: List[port] = inputs or []
        self.outputs: List[port] = outputs or []

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Define the component's behavior at a given time step.

        Parameters
        ----------
        time : float
            Current simulation time.
        inputs : dict
            Mapping from input port names to their current values.
        outputs : dict
            Mapping from output port names to their current values (to be updated).

        This method should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement behavior()")

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name!r})"


class Operation(Component):
    """
    Component that performs an operation (possibly stateless) on inputs to produce outputs.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
    ):
        super().__init__(name=name, inputs=inputs, outputs=outputs)

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Default behavior: override in concrete operations.
        """
        # Example pattern:
        # out_val = some_function_of(inputs)
        # outputs["out"] = out_val
        raise NotImplementedError("Subclasses must implement behavior()")


class Transformation(Component):
    """
    Component that transforms data from inputs to outputs (e.g., unit conversion, mapping).
    This is the internal/model-level transformation, not the LOTTS DSL component.
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        expressions: Optional[List[str]] = None,
    ):
        super().__init__(name=name, inputs=inputs, outputs=outputs)
        self.expressions = expressions or []

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Apply transformation expressions to inputs to compute outputs.
        """
        # Concrete logic will depend on how you encode expressions.
        raise NotImplementedError("Subclasses must implement behavior()")


class Model(Component):
    """
    Base class for model components (e.g., simulation models).

    Supports:
      - Configuration parameters
      - Time-based behavior (simulation steps)
    """

    def __init__(
        self,
        name: str = "",
        inputs: Optional[List[port]] = None,
        outputs: Optional[List[port]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(name=name, inputs=inputs, outputs=outputs)
        self.parameters: Dict[str, Any] = parameters or {}

    def behavior(self, time: float, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """
        Default model behavior: advance the model by one step using current inputs,
        and update outputs.

        Concrete models (FMU, Python, etc.) will override this.
        """
        # Typical pattern:
        #   - set inputs into the underlying model
        #   - call model.advance(...)
        #   - read outputs and populate `outputs` dict
        raise NotImplementedError("Subclasses must implement behavior()")


# -----------------------------------------------------------------------------
# Connections and data transformation / exchange patterns
# -----------------------------------------------------------------------------

class Connector:
    """
    Represents a connection between two components:
      - source component + output port
      - destination component + input port
      - exchange pattern (FIFO, LIFO, etc.)
    """

    def __init__(
        self,
        src_component: str = "",
        src_port: str = "",
        dst_component: str = "",
        dst_port: str = "",
        ex_pattern: Optional["Data_Transformation.Ex_Pattern"] = None,
    ):
        self.src_component = src_component
        self.src_port = src_port
        self.dst_component = dst_component
        self.dst_port = dst_port
        self.ex_pattern = ex_pattern

    def __repr__(self):
        return (
            f"Connector(src={self.src_component}.{self.src_port!r} "
            f"-> dst={self.dst_component}.{self.dst_port!r})"
        )


class Data_Transformation:
    """
    Higher-level abstraction for data transformation and exchange patterns
    between components.
    """

    class Ex_Pattern:
        """
        Exchange pattern defining how data is transferred between components.

        Typical patterns: FIFO, LIFO, LVQ, PQ.
        """

        def __init__(self, pattern_type: str = "FIFO"):
            self.pattern_type = pattern_type

        def transfer(self, source_value: Any) -> Any:
            """
            Apply the exchange pattern to a source value to produce the value
            received at the destination.

            For simple patterns (FIFO/LIFO without buffering), this may just
            return the source value.
            """
            # Concrete logic depends on your pattern implementation.
            return source_value

        def __repr__(self):
            return f"Ex_Pattern(type={self.pattern_type!r})"


class OldEx_Pattern:
    """
    Legacy exchange pattern class (if still used in your codebase).
    Keep this if your execution engine or existing models rely on it.
    """

    def __init__(self, pattern_type: str = "FIFO"):
        self.pattern_type = pattern_type

    def transfer(self, source_value: Any) -> Any:
        # Legacy behavior – adapt as needed.
        return source_value

    def __repr__(self):
        return f"OldEx_Pattern(type={self.pattern_type!r})"

# Backward-compatibility alias for configurable models
# In the new structure, ConfigComp is conceptually the same as Model
ConfigComp = Model
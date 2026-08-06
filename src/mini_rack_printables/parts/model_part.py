from build123d import Solid, Location, Mode, Vector
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PartTreeNode:
    """
    Represents a node in the part tree for a ModelPart.

    Attributes:
        name: Name of the part.
        part: The solid for the part.
        loc: Location of the solid.
        mode: Mode of the solid's addition (i.e. SUBTRACT, ADD)
    """

    name: str
    part: Solid
    loc: Location
    mode: Mode

    def __init__(
        self, name: str, part: Solid, loc: Location = Location(), mode: Mode = Mode.ADD
    ):
        self.name = name
        self.part = part
        self.loc = loc
        self.mode = mode


class ModelPart(ABC):
    """
    Base class for all parts of a Model

    Args:
        label: Label of the part.
        align: Alignment of the part within its division of the plate.
        shift: Shift of the part within its division of the plate.
        padding: Padding around the part with respect to the plate.
    """

    def __init__(self, label: str, align: Vector, shift: Vector, padding: float):
        self.label = label
        self.align = align
        self.shift = shift
        self.padding = padding

    @abstractmethod
    def layout_size(self, plate_size: Vector) -> Vector:
        """
        Return the size of the part for layout purposes.
        """
        pass

    @abstractmethod
    def render(self, plate_size: Vector) -> list[PartTreeNode]:
        """
        Render the feature

        Returns:
            A list of PartTreeNode objects representing the solids to be added to the plate.
        """
        pass

from build123d import Mode, Vector, Plane, Solid, Part, Compound
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..selectors import Place


@dataclass
class Plate:
    """
    Represents a plate on which parts are placed.

    Attributes:
        size: Size of the plate.
        top_plane: The top plane of the plate.
        bottom_plane: The bottom plane of the plate.
    """

    size: Vector
    top_plane: Plane
    bottom_plane: Plane

    def __init__(self, size: Vector, top_plane: Plane, bottom_plane: Plane):
        self.size = size
        self.top_plane = top_plane
        self.bottom_plane = bottom_plane


@dataclass
class PartPiece:
    """
    Represents the output of rendering a ModelPart. It contains the 3d (ie. solid) and
    how to add the solid to the plate (ie. location and combination mode).

    Attributes:
        part: The solid for the part located by the part
        mode: Mode of the solid's addition (i.e. SUBTRACT, ADD)
    """

    part: Solid | Part
    mode: Mode

    def __init__(self, part: Solid | Part, mode: Mode = Mode.ADD):
        self.part = part
        self.mode = mode


class ModelPart(ABC):
    """
    Base class for all parts of a Model

    Args:
        align: Alignment of the part within its division of the plate.
        shift: Shift of the part within its division of the plate.
        padding: Padding around the part with respect to the plate.
    """

    def __init__(self, align: Place, shift: Vector, padding: float):
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
    def render(self, plate: Plate) -> list[PartPiece]:
        """
        Render the feature

        Returns:
            A list of PartOutput objects representing the solids to be added to the plate.
        """
        pass

    def intersect_with(self, other: Part, plate: Plate) -> Compound:
        """
        Intersect this part with another part.
        """
        part_nodes = self.render(plate)
        result = other
        for node in part_nodes:
            if node.mode == Mode.ADD:
                result = result + node.part
            elif node.mode == Mode.SUBTRACT:
                result = result - node.part
            else:
                assert False, "unhandled rendering mode"
        return Compound(result)

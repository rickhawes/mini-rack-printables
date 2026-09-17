from build123d import Mode, Vector, Plane, Solid, Part, Compound
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .part_layouts import PartLayout
from .row_column_collection import RowsColumnsCollection


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


type PlateList = list[Plate] | list[list[Plate]]
"""A 2d list of plates"""


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
    """

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

    @staticmethod
    def render_pieces(parts: PartList, plate: Plate, layout: PartLayout) -> list[PartPiece]:
        """
        Render all `parts` using the given `plate` and `layout` alogrithm.
        """
        pieces = []
        sub_plates = layout.layout_parts(parts, plate)
        for part, _, _, index in RowsColumnsCollection(parts):
            pieces.extend(part.render(sub_plates[index]))
        return pieces

    @staticmethod
    def assemble_pieces(to_part: Part, pieces: list[PartPiece]) -> Compound:
        """
        Intersect `pieces` with `to_part` to create the final result.
        """
        result = to_part
        for piece in pieces:
            if piece.mode == Mode.ADD:
                result = result + piece.part
            elif piece.mode == Mode.SUBTRACT:
                result = result - piece.part
            else:
                assert False, "unhandled rendering mode"
        return Compound(result)


type PartList = list[ModelPart] | list[list[ModelPart]]
"""A row-column list of ModelParts."""

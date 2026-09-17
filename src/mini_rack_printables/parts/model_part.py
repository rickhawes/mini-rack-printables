"""
Classes for sepecifing parts of a `Model`.

"""

from build123d import Mode, Vector, VectorLike, Plane, Solid, Part, Location
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..geometry import Bx


class ModelPart(ABC):
    """
    Base class for all parts of a `Model`. `ModelPart` is used to distinguish this from the build123d `Part` classes
    """

    @dataclass(frozen=True, init=False)
    class DesiredSize:
        """
        Represents the desired size of a `ModelPart` on a plate.
        Contains the minimum size and a flag if the parts wants more space than the minimum size.
        """

        min_size: Vector
        """The minimum size of the plate for rendering."""
        more_x: bool
        """Whether the part wants more space than the minimum size."""
        more_y: bool
        """Whether the part wants more space than the minimum size."""

        def __init__(self, min_size: VectorLike, more_x: bool = False, more_y: bool = False):
            object.__setattr__(self, "min_size", Vector(min_size))
            object.__setattr__(self, "more_x", more_x)
            object.__setattr__(self, "more_y", more_y)

    @abstractmethod
    def desired_size(self) -> DesiredSize:
        """
        Return the desired size of plate for rendering.
        The part will always get at least the minimum size of the plate.

        Returns:
            DesiredSize: The minimum size and the expand flag of the plate for rendering.
        """
        pass

    @abstractmethod
    def render(self, plate_planes: PlatePlanes) -> list[PartPiece]:
        """
        Render the feature

        Returns:
            A list of PartOutput objects representing the solids to be added to the plate.
        """
        pass


type PartList = list[ModelPart] | list[list[ModelPart]]
"""A row-column list of ModelParts."""


@dataclass
class PlatePlanes:
    """
    Represents a plate on which parts are placed during rendering.

    Attributes:
        bounds: The bounds of the plate for that a part can use.
        top_plane: The top plane of the plate for adding to the plate.
        bottom_plane: The bottom plane for removing from the plate.
    """

    bounds: Bx
    top_plane: Plane
    bottom_plane: Plane

    @property
    def size(self) -> Vector:
        """The size of the plate."""
        return self.bounds.size

    @property
    def width(self) -> float:
        """The width of the plate."""
        return self.bounds.size.X

    @property
    def height(self) -> float:
        """The height of the plate."""
        return self.bounds.size.Y

    @property
    def depth(self) -> float:
        """The depth of the plate."""
        return self.bounds.size.Z

    def __init__(self, bounds: Bx, origin_offset: Vector = Vector(0, 0, 0)):
        """
        Initialize the PlatePlanes with the given `bounds` and `origin_offset`.
        """
        if origin_offset.Z != 0:
            raise ValueError("origin_offset.Z must be 0")
        origin = bounds.shift + origin_offset
        self.bottom_plane = Plane.XY.moved(Location((origin.X, origin.Y, bounds.front)))
        self.top_plane = Plane.XY.moved(Location((origin.X, origin.Y, bounds.back)))
        self.bounds = bounds.shifted(-origin_offset)


type PlateList = list[PlatePlanes] | list[list[PlatePlanes]]
"""A 2d list of plates"""


@dataclass
class PartPiece:
    """
    Represents the output of rendering a ModelPart, containing the solid and
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

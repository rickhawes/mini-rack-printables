"""
Classes for sepecifing parts of a `Model`.

"""

from build123d import Mode, Plane, Solid, Part, Location
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..geometry import Bx, Vec2, Vec3


class ModelPart(ABC):
    """
    Base class for all parts of a `Model`. `ModelPart` is used to distinguish this from the build123d `Part` classes
    """

    @dataclass(frozen=True)
    class DesiredSize:
        """
        Represents the desired size of a `ModelPart` on a plate.
        Contains the minimum size and a flag if the parts wants more space than the minimum size.
        """

        min_size: Vec2
        """The minimum size of the plate for rendering."""
        more_x: bool = False
        """Whether the part wants more space than the minimum size."""
        more_y: bool = False
        """Whether the part wants more space than the minimum size."""

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
    def size(self) -> Vec3:
        """The size of the plate."""
        return self.bounds.size

    @property
    def width(self) -> float:
        """The width of the plate."""
        return self.bounds.size.x

    @property
    def height(self) -> float:
        """The height of the plate."""
        return self.bounds.size.y

    @property
    def depth(self) -> float:
        """The depth of the plate."""
        return self.bounds.size.z

    def __init__(self, bounds: Bx, origin_offset: Vec2 = Vec2(0, 0)):
        """
        Initialize the PlatePlanes with the given `bounds` and `origin_offset`.
        """
        origin = bounds.shift.to_2d() + origin_offset
        self.bottom_plane = Plane.XY.moved(Location((origin.x, origin.y, bounds.front)))
        self.top_plane = Plane.XY.moved(Location((origin.x, origin.y, bounds.back)))
        self.bounds = bounds.shifted(Vec3(-origin_offset.x, -origin_offset.y, bounds.shift.z))


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

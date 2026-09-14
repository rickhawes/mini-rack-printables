from collections.abc import Sequence
from enum import Enum, auto
from typing import Literal

from build123d import Axis, Face, Location, Part, Plane, ShapeList, Align


"""
Enums to select placement, faces and edges on shape and the basic functions 
to use these selectors.
"""


# -----------------------------------------------------
# Side selectors
# -----------------------------------------------------
class Side(Enum):
    """
    Enum for selecting a face of a cube or an edge of a square.
    """

    # Face/edge selectors
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()
    BOTTOM = auto()
    BACK = auto()
    FRONT = auto()

    # Aliases for min/max axis values
    MIN_X = LEFT
    MIN_Y = BOTTOM
    MIN_Z = FRONT
    MAX_X = RIGHT
    MAX_Y = TOP
    MAX_Z = BACK


def select_face(faces: ShapeList[Face], side: Side) -> Face:
    """
    Selects a face from the given list of faces based on the selector.
    """
    match side:
        case Side.RIGHT:
            return faces.sort_by(Axis.X)[-1]
        case Side.LEFT:
            return faces.sort_by(Axis.X)[0]
        case Side.TOP:
            return faces.sort_by(Axis.Y)[-1]
        case Side.BOTTOM:
            return faces.sort_by(Axis.Y)[0]
        case Side.BACK:
            return faces.sort_by(Axis.Z)[-1]
        case Side.FRONT:
            return faces.sort_by(Axis.Z)[0]
        case _:
            assert False, f"Invalid face selector: {side}"


def select_faces(part: Part, sides: Sequence[Side]) -> ShapeList[Face]:
    """
    Selects a list of faces from the given list of faces based on the selector.
    """
    return ShapeList([select_face(part.faces(), s) for s in sides])


def select_plane(part: Part, side: Side, flip: bool = False) -> Plane:
    """
    A plane from the given list of faces based on the selector.
    """
    face = select_face(part.faces(), side)
    if flip:
        return Plane(face).reverse()
    else:
        return Plane(face)


def select_planes(part: Part, sides: Sequence[Side], flip: bool = False) -> list[Plane]:
    """
    Selects a list of planes from the given list of faces based on the selector.
    """
    return [select_plane(part, s, flip) for s in sides]


def select_location(part: Part, side: Side, flip: bool = False) -> Location:
    """
    Returns the location of the face selected by the selector.
    """
    return Location(select_plane(part, side, flip))


def select_locations(part: Part, sides: Sequence[Side]) -> list[Location]:
    """
    Forms a list of `Location` objects from the given list of faces based on the selector.
    """
    return [select_location(part, s) for s in sides]


# -----------------------------------------------------
# Place selectors
# -----------------------------------------------------


class Place(Enum):
    """
    Enum for selecting edges and corners of a square.
    """

    # Face/edge
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()
    BOTTOM = auto()

    # Corner of a square
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()
    CENTER = auto()

    # Aliases for min/max axis values
    MIN_X = LEFT
    MIN_Y = BOTTOM
    MAX_X = RIGHT
    MAX_Y = TOP
    NONE = CENTER

    def opposite(self) -> "Place":
        """
        Returns the opposite place reflected through the center.
        """
        conversion = {
            Place.RIGHT: Place.LEFT,
            Place.LEFT: Place.RIGHT,
            Place.TOP: Place.BOTTOM,
            Place.BOTTOM: Place.TOP,
            Place.TOP_RIGHT: Place.BOTTOM_LEFT,
            Place.BOTTOM_RIGHT: Place.TOP_LEFT,
            Place.TOP_LEFT: Place.BOTTOM_RIGHT,
            Place.BOTTOM_LEFT: Place.TOP_RIGHT,
            Place.CENTER: Place.CENTER,
        }
        return conversion[self]

    def is_corner(self) -> bool:
        """
        Returns True if the selector is a corner of a square.
        """
        return self in [
            Place.TOP_RIGHT,
            Place.BOTTOM_RIGHT,
            Place.TOP_LEFT,
            Place.BOTTOM_LEFT,
        ]

    def is_edge(self) -> bool:
        """
        Returns True if the selector is an edge of a square.
        """
        return self in [
            Place.RIGHT,
            Place.LEFT,
            Place.TOP,
            Place.BOTTOM,
        ]

    def as_units(self) -> tuple[int, int]:
        """
        Returns as -1,0,1 values for the place on the square
        """
        conversion = {
            Place.RIGHT: (1, 0),
            Place.LEFT: (-1, 0),
            Place.TOP: (0, 1),
            Place.BOTTOM: (0, -1),
            Place.BOTTOM_LEFT: (-1, -1),
            Place.BOTTOM_RIGHT: (1, -1),
            Place.TOP_LEFT: (-1, 1),
            Place.TOP_RIGHT: (1, 1),
            Place.CENTER: (0, 0),
        }
        assert self in conversion, "Invalid place"
        return conversion[self]

    def as_aligns(self) -> tuple[Align, Align]:
        """
        Returns the place as an alignment tuple
        """

        def unit_to_align(unit: int) -> Align:
            return Align.MAX if unit > 0 else Align.MIN if unit < 0 else Align.CENTER

        x, y = self.as_units()
        return unit_to_align(x), unit_to_align(y)


CornerPlace = Literal[Place.TOP_LEFT, Place.TOP_RIGHT, Place.BOTTOM_LEFT, Place.BOTTOM_RIGHT]
"""The subset of Place that represent corners"""

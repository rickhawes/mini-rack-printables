from collections.abc import Sequence
from enum import Enum, auto

from build123d import Axis, Face, Location, Part, Plane, ShapeList


class Selector(Enum):
    """
    Enum for selecting faces and edges by axis and value.
    """
    # Face/edge selectors
    RIGHT = auto()
    LEFT = auto()
    TOP = auto()
    BOTTOM = auto()
    BACK = auto()
    FRONT = auto()

    # Corner selectors
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()
    CENTER = auto()

    # Aliases for min/max axis values
    MIN_X = LEFT
    MIN_Y = BOTTOM
    MIN_Z = FRONT
    MAX_X = RIGHT
    MAX_Y = TOP
    MAX_Z = BACK
    NONE = CENTER


def select_face(faces: ShapeList[Face], selector: Selector):
    """
    Selects a face from the given list of faces based on the selector.
    """
    match selector:
        case Selector.RIGHT:
            return faces.sort_by(Axis.X)[-1]
        case Selector.LEFT:
            return faces.sort_by(Axis.X)[0]
        case Selector.TOP:
            return faces.sort_by(Axis.Y)[-1]
        case Selector.BOTTOM:
            return faces.sort_by(Axis.Y)[0]
        case Selector.BACK:
            return faces.sort_by(Axis.Z)[-1]
        case Selector.FRONT:
            return faces.sort_by(Axis.Z)[0]
        case _:
            assert False, f"Invalid selector: {selector}"

def select_faces(part: Part, selector: Sequence[Selector]) -> ShapeList[Face]:
    """
    Selects a list of faces from the given list of faces based on the selector.
    """
    return ShapeList([select_face(part.faces(), s) for s in selector])


def select_plane(part: Part, selector: Selector, flip: bool = False) -> Plane:
    """
    A plane from the given list of faces based on the selector.
    """
    face = select_face(part.faces(), selector)
    if flip:
        return Plane(face).reverse()
    else:
        return Plane(face)


def select_planes(part: Part, selector: Sequence[Selector], flip: bool = False) -> list[Plane]:
    """
    Selects a list of planes from the given list of faces based on the selector.
    """
    return [select_plane(part, s, flip) for s in selector]


def select_location(part: Part, selector: Selector) -> Location:
    """
    Returns the location of the face selected by the selector.
    """
    return Location(select_plane(part, selector))


def select_locations(part: Part, selector: Sequence[Selector]) -> list[Location]:
    """
    Forms a list of `Location` objects from the given list of faces based on the selector.
    """
    return [select_location(part, s) for s in selector]

from enum import Enum, auto
from collections.abc import Sequence
from build123d import ShapeList, Face, Axis, Plane, Location, Part


class FaceSelector(Enum):
    """
    Enum for selecting faces by axis and value.
    """

    MAX_X = auto()
    MIN_X = auto()
    MAX_Y = auto()
    MIN_Y = auto()
    MAX_Z = auto()
    MIN_Z = auto()


def select_face(faces: ShapeList[Face], selector: FaceSelector):
    """
    Selects a face from the given list of faces based on the selector.
    """
    match selector:
        case FaceSelector.MAX_X:
            return faces.sort_by(Axis.X)[-1]
        case FaceSelector.MIN_X:
            return faces.sort_by(Axis.X)[0]
        case FaceSelector.MAX_Y:
            return faces.sort_by(Axis.Y)[-1]
        case FaceSelector.MIN_Y:
            return faces.sort_by(Axis.Y)[0]
        case FaceSelector.MAX_Z:
            return faces.sort_by(Axis.Z)[-1]
        case FaceSelector.MIN_Z:
            return faces.sort_by(Axis.Z)[0]


def select_faces(part: Part, selector: Sequence[FaceSelector]) -> ShapeList[Face]:
    """
    Selects a list of faces from the given list of faces based on the selector.
    """
    return ShapeList([select_face(part.faces(), s) for s in selector])


def select_plane(part: Part, selector: FaceSelector, flip: bool = False) -> Plane:
    """
    A plane from the given list of faces based on the selector.
    """
    face = select_face(part.faces(), selector)
    if flip:
        return Plane(face).reverse()
    else:
        return Plane(face)


def select_planes(
    part: Part, selector: Sequence[FaceSelector], flip: bool = False
) -> list[Plane]:
    """
    Selects a list of planes from the given list of faces based on the selector.
    """
    return [select_plane(part, s, flip) for s in selector]


def select_location(part: Part, selector: FaceSelector) -> Location:
    """
    Returns the location of the face selected by the selector.
    """
    return Location(select_plane(part, selector))


def select_locations(part: Part, selector: Sequence[FaceSelector]) -> list[Location]:
    """
    Forms a list of `Location` objects from the given list of faces based on the selector.
    """
    return [select_location(part, s) for s in selector]

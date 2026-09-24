"""
A collection of classes to render the corners of a rectangle.

See Also:
    `RectangleElement` for the corner parameter
"""

from abc import ABC, abstractmethod
from build123d import Vector, Line, RadiusArc, Polyline
from .selectors import Place, CornerPlace


class Corners(ABC):
    """Base class for classes that draw corners of a rectangle"""

    def __init__(self, width: float, height: float | None = None):
        self.width = width
        self.height = height if height is not None else width

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    @abstractmethod
    def draw(self, start: Vector, end: Vector, where: CornerPlace):
        """draw the lines or arcs in the context of `BuildLine`"""
        pass


class RoundedCorners(Corners):
    """Rounded corners"""

    def __init__(self, radius: float):
        self.radius = radius

    def size(self) -> Vector:
        return Vector(self.radius, self.radius)

    def draw(self, start: Vector, end: Vector, where: CornerPlace):
        RadiusArc(start, end, self.radius)


class SquareCorners(Corners):
    """
    Square corners. Square corners are not visible on a rectangle, but they do
    affect the insets in fills.
    """

    def draw(self, start: Vector, end: Vector, where: CornerPlace):
        match where:
            case Place.TOP_LEFT | Place.BOTTOM_RIGHT:
                Polyline(start, (start.X, end.Y), end)
            case Place.TOP_RIGHT | Place.BOTTOM_LEFT:
                Polyline(start, (end.X, start.Y), end)


class InsetCorners(Corners):
    """Inset corners make the rectangle a cross"""

    def draw(self, start: Vector, end: Vector, where: CornerPlace):
        match where:
            case Place.TOP_LEFT | Place.BOTTOM_RIGHT:
                Polyline([start, (end.X, start.Y), end])
            case Place.TOP_RIGHT | Place.BOTTOM_LEFT:
                Polyline([start, (start.X, end.Y), end])


class BeveledCorners(Corners):
    """Beveled corners"""

    def draw(self, start: Vector, end: Vector, where: Place):
        Line(start, end)


class SelectedCorners(Corners):
    """Only draw the selected corners. Use a square corner for the unslected corners"""

    def __init__(
        self,
        corners: Corners,
        top_left: bool = False,
        top_right: bool = False,
        bottom_left: bool = False,
        bottom_right: bool = False,
    ):
        self.corners = corners
        self.is_selected = {
            Place.TOP_LEFT: top_left,
            Place.TOP_RIGHT: top_right,
            Place.BOTTOM_LEFT: bottom_left,
            Place.BOTTOM_RIGHT: bottom_right,
        }
        self.square_corners = SquareCorners(corners.size().X, corners.size().Y)

    def size(self) -> Vector:
        return self.corners.size()

    def draw(self, start: Vector, end: Vector, where: CornerPlace):
        if self.is_selected.get(where, False):
            self.corners.draw(start, end, where)
        else:
            self.square_corners.draw(start, end, where)

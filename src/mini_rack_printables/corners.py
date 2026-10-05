"""
A collection of classes to render the corners of a rectangle.

See Also:
    `RectangleElement` for the corner parameter
"""

from abc import ABC, abstractmethod
from typing import override
from build123d import Vector, Line, RadiusArc, Polyline
from .selectors import Place, CornerPlace
from .geometry import Vec2, Mm


class Corners(ABC):
    """Base class for classes that draw corners of a rectangle"""

    width: Mm
    height: Mm

    def __init__(self, width: Mm, height: Mm | None = None) -> None:
        self.width = width
        self.height = height if height is not None else width

    @property
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @abstractmethod
    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> None:
        """draw the lines or arcs in the context of `BuildLine`"""
        pass


class RoundedCorners(Corners):
    """Rounded corners"""

    radius: Mm

    def __init__(self, radius: Mm) -> None:
        super().__init__(radius, radius)
        self.radius = radius

    @override
    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> None:
        _ = RadiusArc(start_point=start, end_point=end, radius=self.radius)


class SquareCorners(Corners):
    """
    Square corners. Square corners are not visible on a rectangle, but they do
    affect the insets in fills.
    """

    @override
    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> None:
        match where:
            case Place.TOP_LEFT | Place.BOTTOM_RIGHT:
                _ = Polyline(start, (start.X, end.Y), end)
            case Place.TOP_RIGHT | Place.BOTTOM_LEFT:
                _ = Polyline(start, (end.X, start.Y), end)


class InsetCorners(Corners):
    """Inset corners make the rectangle a cross"""

    @override
    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> None:
        match where:
            case Place.TOP_LEFT | Place.BOTTOM_RIGHT:
                _ = Polyline([start, (end.X, start.Y), end])
            case Place.TOP_RIGHT | Place.BOTTOM_LEFT:
                _ = Polyline([start, (start.X, end.Y), end])


class BeveledCorners(Corners):
    """Beveled corners"""

    @override
    def draw(self, start: Vector, end: Vector, where: Place) -> None:
        _ = Line(start, end)


class SelectedCorners(Corners):
    """Only draw the selected corners. Use a square corner for the unselected corners"""

    corners: Corners
    is_selected: dict[Place, bool]
    square_corners: SquareCorners

    def __init__(
        self,
        corners: Corners,
        top_left: bool = False,
        top_right: bool = False,
        bottom_left: bool = False,
        bottom_right: bool = False,
    ) -> None:
        super().__init__(corners.size.x, corners.size.y)
        self.corners = corners
        self.is_selected = {
            Place.TOP_LEFT: top_left,
            Place.TOP_RIGHT: top_right,
            Place.BOTTOM_LEFT: bottom_left,
            Place.BOTTOM_RIGHT: bottom_right,
        }
        self.square_corners = SquareCorners(corners.size.x, corners.size.y)

    @override
    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> None:
        if self.is_selected.get(where, False):
            self.corners.draw(start, end, where)
        else:
            self.square_corners.draw(start, end, where)

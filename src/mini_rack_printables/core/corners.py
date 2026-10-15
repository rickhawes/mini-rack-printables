"""
A collection of classes to render the corners of a rectangle.

See Also:
    `RectangleElement` for the corner parameter
"""

from abc import ABC, abstractmethod
from typing import override
from build123d import Vector, Line, RadiusArc, Polyline
from .geometry import Vec2, Mm


class Corners(ABC):
    """Base class for classes that draw corners of a rectangle"""

    width: Mm
    height: Mm

    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"

    type SelectedCorner = str

    def __init__(self, width: Mm, height: Mm | None = None) -> None:
        self.width = width
        self.height = height if height is not None else width

    @property
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @abstractmethod
    def draw(self, start: Vector, end: Vector, where: Corners.SelectedCorner) -> None:
        """draw the lines or arcs in the context of `BuildLine`"""
        pass


class RoundedCorners(Corners):
    """Rounded corners"""

    radius: Mm

    def __init__(self, radius: Mm) -> None:
        super().__init__(radius, radius)
        self.radius = radius

    @override
    def draw(self, start: Vector, end: Vector, where: Corners.SelectedCorner) -> None:
        _ = RadiusArc(start_point=start, end_point=end, radius=self.radius)


class SquareCorners(Corners):
    """
    Square corners. Square corners are not visible on a rectangle, but they do
    affect the insets in fills.
    """

    @override
    def draw(self, start: Vector, end: Vector, where: Corners.SelectedCorner) -> None:
        match where:
            case Corners.TOP_LEFT | Corners.BOTTOM_RIGHT:
                _ = Polyline(start, (start.X, end.Y), end)
            case Corners.TOP_RIGHT | Corners.BOTTOM_LEFT:
                _ = Polyline(start, (end.X, start.Y), end)
            case _:
                ValueError(f"Corners.draw called with {where}")


class InsetCorners(Corners):
    """Inset corners make the rectangle a cross"""

    @override
    def draw(self, start: Vector, end: Vector, where: Corners.SelectedCorner) -> None:
        match where:
            case Corners.TOP_LEFT | Corners.BOTTOM_RIGHT:
                _ = Polyline([start, (end.X, start.Y), end])
            case Corners.TOP_RIGHT | Corners.BOTTOM_LEFT:
                _ = Polyline([start, (start.X, end.Y), end])
            case _:
                ValueError(f"Corners.draw called with {where}")


class BeveledCorners(Corners):
    """Beveled corners"""

    @override
    def draw(self, start: Vector, end: Vector, where: Corners.SelectedCorner) -> None:
        _ = Line(start, end)


class SelectedCorners(Corners):
    """Only draw the selected corners. Use a square corner for the unselected corners"""

    corners: Corners
    is_selected: dict[Corners.SelectedCorner, bool]
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
            Corners.TOP_LEFT: top_left,
            Corners.TOP_RIGHT: top_right,
            Corners.BOTTOM_LEFT: bottom_left,
            Corners.BOTTOM_RIGHT: bottom_right,
        }
        self.square_corners = SquareCorners(corners.size.x, corners.size.y)

    @override
    def draw(self, start: Vector, end: Vector, where: str) -> None:
        if self.is_selected.get(where, False):
            self.corners.draw(start, end, where)
        else:
            self.square_corners.draw(start, end, where)

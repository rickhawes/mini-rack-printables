"""
Elements are the primitives that make up models and parts. They are built to be easily composable.
"""

from abc import ABC, abstractmethod
import math
from build123d import (
    Rectangle,
    Vector,
    Line,
    Circle,
    RectangleRounded,
    SlotOverall,
    Sketch,
    Face,
    Location,
    Polyline,
    BuildLine,
    make_face,
    BuildSketch,
    Trapezoid,
    Axis,
    Align,
)
from .selectors import Place
from .geometry import Rc
from .fills import Fill
from .corners import Corners, RoundedCorners, SquareCorners


class Element2D(ABC):
    """ABC for the 2d shapes that are used for parts in the rack."""

    @abstractmethod
    def size(self) -> Vector:
        """Returns the size of the shape in 2d."""
        pass

    @abstractmethod
    def sketch(self) -> Sketch:
        """Draw the outline of the shape."""
        pass

    @staticmethod
    def arrange(
        elements: list[Element2D],
        axis: Axis = Axis.X,
        anchor: Place | tuple[Align, Align] = Place.CENTER,
    ) -> list[Location]:
        """
        Arranges a list of elements along an axis, returning their locations.

        Args:
            axis (Axis): The axis along which to arrange the elements.
            anchor (Place | tuple[Align, Align]): The anchor point or alignment for the group of elements.
            elements (list[Element2D]): The list of elements to arrange.

        Returns:
            LocationList: The locations of the arranged elements.
        """
        elem_rects = [Rc(size=element.size()) for element in elements]
        arranged_rects = Rc.arrange(axis, anchor, *elem_rects)
        return [Location(position=rect.shift) for rect in arranged_rects]

    @staticmethod
    def combine(
        elements: list[Element2D],
        axis: Axis = Axis.X,
        anchor: Place | tuple[Align, Align] = Place.CENTER,
    ) -> Sketch:
        """
        Arranges a list of elements along an axis and returns a sketch of their outline.

        Args:
            axis (Axis): The axis along which to arrange the elements.
            anchor (Place | tuple[Align, Align]): The anchor point or alignment for the group of elements.
            elements (list[Element2D]): The list of elements to arrange.

        Returns:
            Sketch: The sketch of the arranged elements.
        """
        locations = Element2D.arrange(elements, axis, anchor)
        sketch = Sketch()
        for element, location in zip(elements, locations):
            sketch += element.sketch().move(location)
        return sketch


class CircleElement(Element2D):
    """A circle element."""

    def __init__(self, radius: float):
        """
        Args:
            radius (float): The radius of the circle.
        """
        self.radius = radius

    def size(self) -> Vector:
        return Vector(2 * self.radius, 2 * self.radius)

    def sketch(self) -> Sketch:
        return Circle(self.radius)


class RectangleElement(Element2D):
    """A rectangle shape or rounded rectangle shape."""

    def __init__(
        self,
        width: float,
        height: float,
        corners: float | int | Corners | None = None,
        fill: Fill | None = None,
    ):
        """
        Args:
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            corners (Corners): The corner shape of the rectangle.
                If a `float` > 0, then a Rounded Corner is used.
            fill (Holes): The hole pattern for the inside of the rectangle after
                insetting the rectangle for the corner size. Defaults to Fill.SOLID.
        """
        self.width = width
        self.height = height
        if isinstance(corners, (int, float)):
            self.corners = RoundedCorners(corners)
        elif corners is None:
            self.corners = SquareCorners(0)
        else:
            self.corners = corners
        self.fill = fill

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        def solid_fill() -> Sketch:
            """Sketch the rectangle with its corners"""
            # Optimize for square and rounded corners
            match self.corners:
                case SquareCorners():
                    return Rectangle(self.width, self.height)
                case RoundedCorners() if self.corners.radius == 0:
                    return Rectangle(self.width, self.height)
                case RoundedCorners():
                    return RectangleRounded(self.width, self.height, self.corners.radius)
                case _:
                    return complex_corners()

        def complex_corners() -> Sketch:
            cs = self.corners.size()
            cw, ch = cs.X, cs.Y
            dx, dy = (self.width / 2) - cw, (self.height / 2) - ch
            with BuildSketch() as sk:
                with BuildLine():
                    # side lines
                    l_top = Line((-dx, dy + ch), (dx, dy + ch))
                    l_right = Line((dx + cw, dy), (dx + cw, -dy))
                    l_bottom = Line((dx, -dy - ch), (-dx, -dy - ch))
                    l_left = Line((-dx - cw, -dy), (-dx - cw, dy))
                    # corners
                    self.corners.draw(l_top @ 1, l_right @ 0, Place.TOP_RIGHT)
                    self.corners.draw(l_right @ 1, l_bottom @ 0, Place.BOTTOM_RIGHT)
                    self.corners.draw(l_bottom @ 1, l_left @ 0, Place.BOTTOM_LEFT)
                    self.corners.draw(l_left @ 1, l_top @ 0, Place.TOP_LEFT)
                make_face()
            return sk.sketch

        def hole_fill() -> Sketch:
            assert self.fill, "fill must be provided"
            # make a sketch of the holes
            #
            cs = self.corners.size()
            inner_dx, inner_dy = self.width - 2 * cs.X, self.height - 2 * cs.Y
            outline = solid_fill().wire()
            holes = self.fill.locations(inner_dx, inner_dy) * self.fill.sketch().wire()
            sk = Sketch()
            sk += Face(outline, holes)
            return sk

        if self.fill:
            return hole_fill()
        else:
            return solid_fill()


class SlotElement(Element2D):
    """A slot shape."""

    def __init__(self, width: float, height: float):
        """
        Args:
            width (float): The width of the slot.
            height (float): The height of the slot.
        """
        self.width = width
        self.height = height

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        return SlotOverall(self.width, self.height)


class TrapezoidElement(Element2D):
    """A trapezoid shape with the major width on the bottom and minor on the top."""

    def __init__(
        self,
        width: float,
        height: float,
        angle1: float | None = 90,
        angle2: float | None = None,
        minor_width: float | None = None,
        rotate: float = 0,
    ):
        """
        A trapezoid shape with the major width on the bottom and minor on the top.

        Args:
            width (float): The major width of the trapezoid.
            height (float): The height of the trapezoid.
            angle1 (float): The interior angle of the first side. Defaults to 90.
            angle2 (float): The interior angle of the second side. Defaults to symmetrical to angle1.
            minor_width (float): The width of the minor side. Defaults to None.
            rotation (bool): Whether to rotate the trapezoid. Defaults to False.
        """
        if angle1 is not None and angle2 is not None and minor_width is not None:
            raise ValueError("angle1, angle2, and minor_width cannot all be set")
        if angle1 is None and angle2 is None and minor_width is None:
            raise ValueError("angle1, angle2, and minor_width cannot all be None")

        if minor_width is not None:
            # Calculate angle1 or angle2 based on minor_width
            if angle1 is not None and angle2 is None:
                reduction_left = 0 if angle1 == 90 else height / math.tan(math.radians(angle1))
                angle2 = math.degrees(math.atan(height / (width - minor_width - reduction_left)))
            elif angle1 is None and angle2 is not None:
                reduction_right = 0 if angle2 == 90 else height / math.tan(math.radians(angle2))
                angle1 = math.degrees(math.atan(height / (width - minor_width - reduction_right)))
            else:
                angle1 = angle2 = math.degrees(math.atan(2 * height / (width - minor_width)))
        if angle2 is not None and angle1 is None:
            angle1 = angle2
        assert angle1 is not None, "angle1 could not be calculated"

        self.width = width
        self.height = height
        self.angle1 = angle1
        self.angle2 = angle2
        self.rotate = rotate

    def size(self) -> Vector:
        dx = self.height * math.sin(math.radians(self.rotate)) + self.width * math.cos(
            math.radians(self.rotate)
        )
        dy = self.height * math.cos(math.radians(self.rotate)) + self.width * math.sin(
            math.radians(self.rotate)
        )
        return Vector(dx, dy)

    def sketch(self) -> Sketch:
        return Trapezoid(
            self.width,
            self.height,
            left_side_angle=self.angle1,
            right_side_angle=self.angle2,
            rotation=self.rotate,
        )


class RightTriangleElement(Element2D):
    """A right triangle shape."""

    def __init__(self, width: float, height: float, flip: bool = False):
        """
        Args:
            width (float): The width of the triangle.
            height (float): The height of the triangle.
        """
        self.width = width
        self.height = height
        self.flip = flip

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        dx, dy = self.width / 2, self.height / 2
        pts = (
            [(-dx, -dy), (-dx, dy), (dx, -dy)] if self.flip else [(-dx, -dy), (dx, dy), (dx, -dy)]
        )
        return make_face(Polyline(pts, close=True))

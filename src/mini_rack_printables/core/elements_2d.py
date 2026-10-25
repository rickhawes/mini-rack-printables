"""
2d Elements for models. Elements are the primitives that make up models and parts. They are built to be easily combined and rendered.
"""

import math
from abc import ABC, abstractmethod
from typing import override

from build123d import (
    BuildLine,
    BuildSketch,
    Circle,
    Face,
    Line,
    Location,
    Polyline,
    Rectangle,
    RectangleRounded,
    Sketch,
    SlotOverall,
    Trapezoid,
    make_face,
    offset,
)

from .corners import Corners, RoundedCorners, SquareCorners
from .geometry import Ax2, AxDir, Mm, Rc, Vec2
from .hole_patterns import HolePattern
from .print_dims import E


class Element2D(ABC):
    """ABC for the 2d shapes that are used for parts."""

    @property
    @abstractmethod
    def size(self) -> Vec2:
        """Returns the size of the shape in 2d."""

    @abstractmethod
    def sketch(self) -> Sketch:
        """Draw the outline of the shape."""


class CircleElement(Element2D):
    """A circle element"""

    radius: Mm

    def __init__(self, radius: Mm) -> None:
        """
        Args:
            radius (Mm): The radius of the circle.
        """
        self.radius = radius

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(2 * self.radius, 2 * self.radius)

    @override
    def sketch(self) -> Sketch:
        return Circle(self.radius)


class RectangleElement(Element2D):
    """A rectangle shape or rounded rectangle shape."""

    width: Mm
    height: Mm
    corners: Corners
    holes: HolePattern | None

    def __init__(
        self,
        width: Mm,
        height: Mm,
        corners: Mm | Corners | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        """
        Args:
            width (Mm): The width of the rectangle.
            height (Mm): The height of the rectangle.
            corners (Corners): The corner shape of the rectangle.
                If a `Mm` > 0, then a Rounded Corner is used.
            holes (HolePattern): The hole pattern for the inside of the rectangle after
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
        self.holes = holes

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
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
            cs = self.corners.size
            cw, ch = cs.x, cs.y
            dx, dy = (self.width / 2) - cw, (self.height / 2) - ch
            with BuildSketch() as sk:
                with BuildLine():
                    # side lines
                    l_top = Line((-dx, dy + ch), (dx, dy + ch))
                    l_right = Line((dx + cw, dy), (dx + cw, -dy))
                    l_bottom = Line((dx, -dy - ch), (-dx, -dy - ch))
                    l_left = Line((-dx - cw, -dy), (-dx - cw, dy))
                    # corners
                    self.corners.draw(l_top @ 1, l_right @ 0, Corners.TOP_RIGHT)
                    self.corners.draw(l_right @ 1, l_bottom @ 0, Corners.BOTTOM_RIGHT)
                    self.corners.draw(l_bottom @ 1, l_left @ 0, Corners.BOTTOM_LEFT)
                    self.corners.draw(l_left @ 1, l_top @ 0, Corners.TOP_LEFT)
                _ = make_face()
            return Sketch(sk.sketch)

        def hole_fill() -> Sketch:
            assert self.holes is not None, "fill must be provided"
            # make a sketch of the holes
            #
            outline = solid_fill().wire()
            holes = self.holes.locations(self.size, self.corners.size) * self.holes.sketch().wire()
            sk = Sketch()
            sk += Face(outline, holes)
            return sk

        if self.holes is None:
            return solid_fill()
        else:
            return hole_fill()


class SlotElement(Element2D):
    """A slot shape."""

    width: Mm
    height: Mm

    def __init__(self, width: Mm, height: Mm) -> None:
        """
        Args:
            width (Mm): The width of the slot.
            height (Mm): The height of the slot.
        """
        self.width = width
        self.height = height

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
    def sketch(self) -> Sketch:
        return SlotOverall(self.width, self.height)


class TrapezoidElement(Element2D):
    """A trapezoid shape with the major width on the bottom and minor on the top."""

    width: Mm
    height: Mm
    angle1: float
    angle2: float | None = None
    minor_width: Mm | None = None
    rotate: float = 0

    def __init__(
        self,
        width: Mm,
        height: Mm,
        angle1: float | None = 90,
        angle2: float | None = None,
        minor_width: Mm | None = None,
        rotate: Mm = 0,
    ) -> None:
        """
        A trapezoid shape with the major width on the bottom and minor on the top.

        Args:
            width (Mm): The major width of the trapezoid.
            height (Mm): The height of the trapezoid.
            angle1 (Mm): The interior angle of the first side. Defaults to 90.
            angle2 (Mm): The interior angle of the second side. Defaults to angle1.
            minor_width (Mm): The width of the minor side. Defaults to None.
            rotate (bool): Whether to rotate the trapezoid. Defaults to False.
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

    @property
    @override
    def size(self) -> Vec2:
        dx = self.height * math.sin(math.radians(self.rotate)) + self.width * math.cos(
            math.radians(self.rotate)
        )
        dy = self.height * math.cos(math.radians(self.rotate)) + self.width * math.sin(
            math.radians(self.rotate)
        )
        return Vec2(dx, dy)

    @override
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

    width: Mm
    height: Mm
    flip: bool

    def __init__(self, width: Mm, height: Mm, flip: bool = False) -> None:
        """
        Args:
            width (Mm): The width of the triangle.
            height (Mm): The height of the triangle.
        """
        self.width = width
        self.height = height
        self.flip = flip

    @property
    @override
    def size(self) -> Vec2:
        return Vec2(self.width, self.height)

    @override
    def sketch(self) -> Sketch:
        dx, dy = self.width / 2, self.height / 2
        pts = [(-dx, -dy), (-dx, dy), (dx, -dy)] if self.flip else [(-dx, -dy), (dx, dy), (dx, -dy)]
        return make_face(Polyline(pts, close=True))


class AlignedElement(Element2D):
    """A combined element shape"""

    elements: list[Element2D]
    axis: Ax2
    align: AxDir

    def __init__(
        self, elements: list[Element2D], axis: Ax2 = Ax2.X, align: AxDir = AxDir.CENTER
    ) -> None:
        self.elements = elements
        self.axis = axis
        self.align = align

    @property
    @override
    def size(self) -> Vec2:
        if self.axis == Ax2.X:
            return Vec2(sum(e.size.x for e in self.elements), max(e.size.y for e in self.elements))
        else:
            return Vec2(max(e.size.x for e in self.elements), sum(e.size.y for e in self.elements))

    def arrange(self) -> list[Location]:
        """
        Arranges a list of elements along an axis, returning their locations.
        """
        elem_rects = [Rc(el.size) for el in self.elements]
        arranged_rects = Rc.arrange(self.axis, self.align, *elem_rects)
        return [Location(position=rect.center.to_vector()) for rect in arranged_rects]

    @override
    def sketch(self) -> Sketch:
        locations = self.arrange()
        moved_elements: list[Sketch] = [
            locations[i] * self.elements[i].sketch() for i in range(len(locations))
        ]
        # do the fusing all at once
        return Sketch(moved_elements)


class LocatedElement(Element2D):
    """An element formed by list of elements with independent locations.

    Args:
        elements (list[Element2D]): The list of elements or a single element that is repeated.
        locations (list[Location]): The list of locations.
    """

    elements: list[Element2D]
    locations: list[Vec2]
    _union_rc: Rc

    def __init__(self, elements: list[Element2D] | Element2D, locations: list[Vec2]) -> None:
        if not isinstance(elements, list):
            elements = [elements] * len(locations)
        if len(elements) != len(locations):
            raise ValueError("locations and elements must have the same length")
        self.elements = elements
        self.locations = locations
        rcs = [Rc(e.size, l) for e, l in zip(self.elements, self.locations)]
        self._union_rc = Rc.union(*rcs)

    @property
    def size(self) -> Vec2:
        return self._union_rc.size

    def sketch(self) -> Sketch:
        moved_elements: list[Sketch] = [
            Location((l - self._union_rc.center).to_vector()) * e.sketch()
            for e, l in zip(self.elements, self.locations)
        ]
        return Sketch(moved_elements)


class CutoutElement(Element2D):
    """Create an element that has a `base` with a `cutout` elements"""

    base: Element2D
    cutout: Element2D
    cutout_offset: Vec2

    def __init__(self, base: Element2D, cutout: Element2D, offset: Vec2 | None = None) -> None:
        if offset is None:
            offset = Vec2(0, 0)
        if not Rc(cutout.size, offset).is_within(Rc(base.size)):
            raise ValueError("cutout must be within base")
        self.base = base
        self.cutout = cutout
        self.cutout_offset = offset

    @property
    def size(self) -> Vec2:
        return self.base.size

    def sketch(self) -> Sketch:
        return Sketch(
            self.base.sketch() - Location(self.cutout_offset.to_vector()) * self.cutout.sketch()
        )


class RingElement(Element2D):
    """Create an element that has a `base` with a `cutout` elements"""

    base: Element2D
    """The base shape"""
    outset: Mm
    """The outset amount (may be negative for an inset)"""

    def __init__(self, base: Element2D, outset: Mm) -> None:
        if abs(outset) < E:
            raise ValueError("outset must not be 0")
        self.base = base
        self.outset = outset

    @property
    def size(self) -> Vec2:
        return (
            self.base.size
            if self.outset < 0
            else self.base.size + Vec2(2 * self.outset, 2 * self.outset)
        )

    def sketch(self) -> Sketch:
        base = self.base.sketch()
        outset = offset(base, self.outset)
        inner, outer = (base, outset) if self.outset < 0 else (outset, base)
        return Sketch(outer - inner)

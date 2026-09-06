from abc import ABC, abstractmethod
import math
from enum import Enum, auto
from build123d import (
    Rectangle,
    Vector,
    VectorLike,
    Line,
    Circle,
    RadiusArc,
    RectangleRounded,
    SlotOverall,
    Sketch,
    extrude,
    offset,
    Part,
    Face,
    Plane,
    Location,
    Polyline,
    BuildLine,
    mirror,
    make_face,
    BuildSketch,
    Trapezoid,
    HexLocations,
    RegularPolygon,
)

from .selectors import (
    select_plane,
    Place,
    Side,
    has_top_right_corner,
    has_bottom_right_corner,
    has_top_left_corner,
    has_bottom_left_corner,
)


# --------------------------------------------------------
# 2D Elements
# --------------------------------------------------------


class FillPattern(Enum):
    """The type of hole to use fora fill."""

    SOLID = auto()
    """No holes, the plate is solid."""
    HEX = auto()
    """Hexagonal holes."""
    CIRCULAR = auto()
    """Circular holes."""


class FillDimensions:
    WIDTH = 0.5
    SPACING = 4.0


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

    def locate(self, other: Element2D, where: Place, outside: bool = False) -> Location:
        """
        Returns the alignment position for the edge of this element relative to the given element.

        Args:
            other (Element): The element for which the calculation is made
            edge (Selector): Which edge or corner of this element to align on.
            outside (bool): Whether to align the `other` element outside the boundary of this element.

        Returns:
            Pos: The alignment position for `other` element relative to this element.
        """
        raise NotImplementedError


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
        radius: float = 0,
        fill: FillPattern = FillPattern.SOLID,
    ):
        """
        Args:
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            radius (float, optional): The radius of the rounded corners. Defaults to 0.
            fill (Fill): The fill pattern of the rectangle. Defaults to Fill.SOLID
        """
        self.width = width
        self.height = height
        self.radius = radius
        self.fill = fill

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        def solid_fill() -> Sketch:
            if self.radius > 0:
                return RectangleRounded(self.width, self.height, self.radius)
            else:
                return Rectangle(self.width, self.height)

        def hole_fill() -> Sketch:
            # make a sketch of
            inner_dx, inner_dy = self.width - self.radius, self.height - self.radius
            spacing, width = FillDimensions.SPACING, FillDimensions.WIDTH

            assert inner_dx > 2 * spacing and inner_dy > 2 * spacing, (
                "Hex plate size must be larger than the hex spacing"
            )
            outline = solid_fill().wire()
            hole_locs = HexLocations(
                spacing,
                math.floor(inner_dx / (2 * spacing)),
                math.floor(inner_dy / (2 * spacing)) - 1,
            )
            if self.fill == FillPattern.HEX:
                holes = hole_locs * RegularPolygon(spacing - width, 6).wire()
            elif self.fill == FillPattern.CIRCULAR:
                holes = hole_locs * Circle(spacing - width / 2).wire()
            sk = Sketch()
            sk += Face(outline, holes)
            return sk

        match self.fill:
            case FillPattern.SOLID:
                return solid_fill()
            case FillPattern.HEX | FillPattern.CIRCULAR:
                return hole_fill()


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


class CrossElement(Element2D):
    """A cross shape."""

    def __init__(self, width: float, height: float, corner_width: float, corner_height: float):
        """
        Args:
            width (float): The overall width of the cross.
            height (float): The overall height of the cross.
            corner_width (float): The width of the corner.
            corner_height (float): The height of the corner.
        """
        self.width = width
        self.height = height
        self.corner_width = corner_width
        self.corner_height = corner_height

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        dx = self.width / 2 - self.corner_width
        dy = self.height / 2 - self.corner_height
        cw = self.corner_width
        ch = self.corner_height

        with BuildSketch() as sk:
            with BuildLine():
                # Draw one quadrant of the outline using Polyline
                Polyline((0, dy + ch), (dx, dy + ch), (dx, dy), (dx + cw, dy), (dx + cw, 0))
                # Mirror the outline
                mirror(about=Plane.YZ)
                mirror(about=Plane.XZ)
            make_face()
        return sk.sketch


class RectangleWithCornersElement(Element2D):
    """
    Element for a rectangle with explicit rounded corners.
    """

    def __init__(self, width: float, height: float, radius: float, corners: list[Place]):
        """
        Args:
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            radius (float): The radius of the rounded corners.
            corners (list[Selector]): The corners to round.
        """
        assert radius > 0, "radius must be greater than 0"
        self.width = width
        self.height = height
        self.radius = radius
        self.corners = corners

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        r = self.radius
        dx = (self.width / 2) - r
        dy = (self.height / 2) - r
        with BuildSketch() as sk:
            with BuildLine():
                # top line
                l_top = Line((-dx, dy + r), (dx, dy + r))
                l_right = Line((dx + r, dy), (dx + r, -dy))
                l_bottom = Line((dx, -dy - r), (-dx, -dy - r))
                l_left = Line((-dx - r, -dy), (-dx - r, dy))
                # top_right corner
                if has_top_right_corner(self.corners):
                    RadiusArc(l_top @ 1, l_right @ 0, radius=r)
                else:
                    Line(l_top @ 1, (dx + r, dy + r))
                    Line((dx + r, dy + r), l_right @ 0)
                # bottom_right corner
                if has_bottom_right_corner(self.corners):
                    RadiusArc(l_right @ 1, l_bottom @ 0, radius=r)
                else:
                    Line(l_right @ 1, (dx + r, -dy - r))
                    Line((dx + r, -dy - r), l_bottom @ 0)
                # bottom_left corner
                if has_bottom_left_corner(self.corners):
                    RadiusArc(l_bottom @ 1, l_left @ 0, radius=r)
                else:
                    Line(l_bottom @ 1, (-dx - r, -dy - r))
                    Line((-dx - r, -dy - r), l_left @ 0)
                # top_left corner
                if has_top_left_corner(self.corners):
                    RadiusArc(l_left @ 1, l_top @ 0, radius=r)
                else:
                    Line(l_left @ 1, (-dx - r, dy + r))
                    Line((-dx - r, dy + r), l_top @ 0)
            make_face()
        return sk.sketch


class TrapezoidElement(Element2D):
    """A trapezoid shape or rounded rectangle shape."""

    def __init__(self, width: float, height: float, angle1: float = 90, angle2: float = 90):
        """
        Args:
            width (float): The width of the rectangle.
            height (float): The height of the rectangle.
            angle1 (float): The interior angle of the first side. Defaults to 90.
            angle2 (float): The interior angle of the second side. Defaults to 90.
        """
        self.width = width
        self.height = height
        self.angle1 = angle1
        self.angle2 = angle2

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def sketch(self) -> Sketch:
        return Trapezoid(
            self.width, self.height, left_side_angle=self.angle1, right_side_angle=self.angle2
        )


# --------------------------------------------------------
# 3D Elements
# --------------------------------------------------------


class Element3D(Element2D):
    """Element for 3d shapes"""

    @abstractmethod
    def size(self) -> Vector:
        """Returns the size of the shape in 3d."""
        pass

    @abstractmethod
    def extrude(self) -> Part:
        """Extrudes the shape along the z-axis."""
        pass

    @abstractmethod
    def on(self, selector: Place) -> Plane:
        """Returns the plane for the element."""
        pass

    def place(
        self,
        other: Element3D,
        where: Place,
        outside: bool = False,
        on: Place | Plane | None = None,
    ) -> Part:
        """
        Returns the alignment position for the edge of this element relative to the given element.

        Args:
            other (Element): The element for which the calculation is made
            edge (Selector): Which edge or corner of this element to align on.
            outside (bool): Whether to align the `other` element outside the boundary of this element.

        Returns:
            Pos: The alignment position for `other` element relative to this element.
        """
        raise NotImplementedError


def _plane_from_over_under(
    over: Part | Face | None, under: Part | Face | None, amount: float
) -> Plane:
    """
    Helper to get the plane from the on_top_of argument.

    Args:
        over (Part | Face | None): The part or face to place the element over.
        under (Part | Face | None): The part or face to place the element under.
        amount (float): The amount to extrude the element.

    Returns:
        Plane: The plane to extrude the element on.
    """
    if over is None and under is None:
        return Plane.XY
    elif isinstance(over, Face) and under is None:
        return Plane(over)
    elif over is None and isinstance(under, Face):
        return Plane(Plane(under) * Location((0, 0, -amount)))
    elif isinstance(over, Part) and under is None:
        return select_plane(over, Side.MAX_Z)
    elif over is None and isinstance(under, Part):
        return Plane(select_plane(under, Side.MIN_Z) * Location((0, 0, -amount)))
    else:
        assert False, "Invalid over and under combination"


def PrismElement(Element3D):
    """A prism element."""

    def __init__(self, element: Element2D, amount: float):
        self.element = element
        self.amount = amount

    def size(self) -> Vector:
        size2d = self.element.size()
        return Vector(size2d.X, size2d.Y, self.amount)

    def extrude(self) -> Part:
        return self.element.sketch()


def extrude_element(
    element: Element2D,
    amount: float,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a basic prism from the element shape.
    The extrusion is done from the XY plane or the MAX_Z of the on_top_of part.

    Args:
        shape (PrimativeShape): The shape of the prism.
        amount (float): The amount to extrude the prism in the Z direction.
        on_top_of (Part | Face | None, optional): The plane to extrude on top of. Defaults to XY.

    Returns:
        Part: The extruded prism of the basic shape.
    """
    return _plane_from_over_under(over, under, amount) * extrude(element.sketch(), amount)


def sketch_ring(element: Element2D, wall_thickness: float) -> Sketch:
    """
    Make a 2d ring from the element shape.

    Args:
        shape (PrimativeShape): The shape of the ring.
        wall_thickness (float): The thickness of the ring wall.
        on_top_of (Part | Face | None, optional): The plane to extrude on top of. Defaults to XY.

    Returns:
        Part: The extruded ring of the basic shape.
    """
    inner = element.sketch()
    outer = offset(inner, wall_thickness)
    return Sketch(outer - inner)


def extrude_tube(
    element: Element2D,
    wall_thickness: float,
    amount: float,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a 3d tube from the element shape by outsetting the shape and extruding it along the Z axis.

    Args:
        shape (PrimativeShape): The shape of the tube.
        wall_thickness (float): The thickness of the tube wall.
        amount (float): The amount to extrude the tube in the Z direction.
        over (Part | Face | None, optional): The plane to place the tube over. Defaults to XY.
        under (Part | Face | None, optional): The plane to place the tube under. Cannot be specified with `over`.
    Returns:
        Part: The extruded tube of the basic shape.
    """
    plane = _plane_from_over_under(over, under, amount)
    sketch = sketch_ring(element, wall_thickness)
    return plane * extrude(sketch, amount)


def extrude_sketch(
    sketch: Sketch,
    amount: float,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Extrude a sketch along the Z axis.

    Args:
        sketch (Sketch): The sketch to extrude.
        amount (float): The amount to extrude the sketch in the Z direction.
        over (Part | Face | None, optional): The plane to place the sketch over. Defaults to XY.
        under (Part | Face | None, optional): The plane to place the sketch under. Cannot be specified with `over`.
    Returns:
        Part: The extruded sketch.
    """
    return _plane_from_over_under(over, under, amount) * extrude(sketch, amount)


def make_plate(size: VectorLike, fill: FillPattern = FillPattern.SOLID) -> Part:
    """
    Make a plate of the given size and fill pattern.

    Args:
        size (VectorLike): The size of the plate.
        fill (FillPattern, optional): The fill pattern of the plate. Defaults to SOLID.

    Returns:
        Part: The extruded plate.
    """
    _size = Vector(size)
    sketch = RectangleElement(_size.X, _size.Y, fill=fill).sketch()
    return extrude(sketch, _size.Z)

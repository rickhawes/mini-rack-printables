from abc import ABC, abstractmethod
import math
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
    LocationList,
    Polyline,
    BuildLine,
    make_face,
    BuildSketch,
    Trapezoid,
    HexLocations,
    RegularPolygon,
    GridLocations,
    Wire,
)
from .selectors import select_plane, Place, Side, CornerPlace


# --------------------------------------------------------
# Hole Fills
# --------------------------------------------------------


class Holes(ABC):
    """Some elements can support holes"""

    def __init__(self, spacing, width):
        """Initialize with `spacing` between holes and `width` of the fill between holes."""
        self.s = spacing
        self.w = width

    @abstractmethod
    def locations(self, dx, dy) -> LocationList:
        """Return the locations of the holes for the given dimensions."""
        pass

    @abstractmethod
    def sketch(self) -> Sketch:
        """Sketch a single hole."""
        pass


class HexHoles(Holes):
    """Hexagonal holes."""

    def __init__(self, spacing: float = 4.0, width: float = 1.0):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        x_count, y_count = math.floor(dx / (2 * self.s)), math.floor((dy - self.s) / (2 * self.s))
        assert x_count > 0 and y_count > 0, f"Must have a few holes {dx, dy, x_count, y_count}"
        return HexLocations(self.s, x_count, y_count)

    def sketch(self) -> Sketch:
        return RegularPolygon(self.w - self.s, 6)


class CircleHoles(Holes):
    """Circular holes."""

    def __init__(self, spacing: float = 3.0, width: float = 1.5):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        return HexLocations(
            self.s, math.floor(dx / (2 * self.s)), math.floor((dy - self.s) / (2 * self.s))
        )

    def sketch(self) -> Sketch:
        return Circle(self.s - self.w / 2)


class SquareHoles(Holes):
    """Square holes."""

    def __init__(self, spacing: float = 4.0, width: float = 1.0):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        return GridLocations(self.s, self.s, math.floor(dx / self.s), math.floor(dy / self.s))

    def sketch(self) -> Sketch:
        return Rectangle(self.s - self.w, self.s - self.w)


# --------------------------------------------------------
# Corner classes
# --------------------------------------------------------


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

    def draw(self, start: Vector, end: Vector, where: CornerPlace) -> Wire:
        if self.is_selected.get(where, False):
            return self.corners.draw(start, end, where)
        else:
            return self.square_corners.draw(start, end, where)


# --------------------------------------------------------
# 2D Elements
# --------------------------------------------------------


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
        corners: float | int | Corners | None = None,
        fill: Holes | None = None,
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


def make_plate(size: VectorLike, fill: Holes | None = None) -> Part:
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

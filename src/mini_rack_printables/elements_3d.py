"""
Elements 3D

Elements are the primitives that make up models and parts. They are built to be easily composable.
"""
from abc import abstractmethod
from build123d import (
    Vector,
    VectorLike,
    Sketch,
    extrude,
    offset,
    Part,
    Face,
    Plane,
    Location,
)
from .selectors import select_plane, Place, Side
from .elements_2d import Element2D, RectangleElement, Fill


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


def make_plate(size: VectorLike, fill: Fill | None = None) -> Part:
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

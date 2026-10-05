"""
3D Elements for models and parts. Elements are the primitives that are to form a model.

See Also:
    Elements2d - for the two equivalent
"""

from abc import ABC, abstractmethod
from typing import override
from build123d import (
    Sketch,
    extrude,
    offset,
    Part,
    Face,
    Plane,
    Location,
)
from .selectors import select_plane, Place, Side
from .elements_2d import Element2D, RectangleElement
from .fills import Fill
from .geometry import Vec3, Mm


class Element3D(ABC):
    """Element for 3d shapes"""

    @abstractmethod
    def size(self) -> Vec3:
        """Returns the size of the shape in 3d."""
        pass

    @abstractmethod
    def extrude(self) -> Part:
        """Extrudes the shape along the z-axis."""
        pass

    @abstractmethod
    def plane_on(self, selector: Place) -> Plane:
        """Returns the plane for the element."""
        pass


def _plane_from_over_under(
    over: Part | Face | None, under: Part | Face | None, amount: Mm
) -> Plane:
    """
    Helper to get the plane from the on_top_of argument.

    Args:
        over (Part | Face | None): The part or face to place the element over.
        under (Part | Face | None): The part or face to place the element under.
        amount (Mm): The amount to extrude the element.

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


class PrismElement(Element3D):
    """A prism element."""

    element: Element2D
    amount: Mm

    def __init__(self, element: Element2D, amount: Mm) -> None:
        self.element = element
        self.amount = amount

    @override
    def plane_on(self, selector: Place) -> Plane:
        raise NotImplementedError

    @override
    def size(self) -> Vec3:
        size2d = self.element.size()
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def extrude(self) -> Part:
        return extrude(self.element.sketch())


def extrude_element(
    element: Element2D,
    amount: Mm,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a basic prism from the element shape.
    The extrusion is done from the XY plane or the MAX_Z of the on_top_of part.

    Args:
        element (Element2D): The shape of the prism.
        amount (Mm): The amount to extrude the prism in the Z direction.
        over (Part | Face | None, optional): The plane to extrude on top of. Defaults to XY.
        under (Part | Face | None, optional): The plane to extrude under. Defaults to None.

    Returns:
        Part: The extruded prism of the basic shape.
    """
    return _plane_from_over_under(over, under, amount) * extrude(element.sketch(), amount)


def sketch_ring(element: Element2D, wall_thickness: Mm) -> Sketch:
    """
    Make a 2d ring from the element shape.

    Args:
        element (Element2D): The shape of the ring.
        wall_thickness (Mm): The thickness of the ring wall.

    Returns:
        Part: The extruded ring of the basic shape.
    """
    inner = element.sketch()
    outer = offset(inner, wall_thickness)
    return Sketch(outer - inner)


def extrude_tube(
    element: Element2D,
    wall_thickness: Mm,
    amount: Mm,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a 3d tube from the element shape by outsetting the shape and extruding it along the Z axis.

    Args:
        element (Element2D): The shape of the tube.
        wall_thickness (Mm): The thickness of the tube wall.
        amount (Mm): The amount to extrude the tube in the Z direction.
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
    amount: Mm,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Extrude a sketch along the Z axis.

    Args:
        sketch (Sketch): The sketch to extrude.
        amount (Mm): The amount to extrude the sketch in the Z direction.
        over (Part | Face | None, optional): The plane to place the sketch over. Defaults to XY.
        under (Part | Face | None, optional): The plane to place the sketch under. Cannot be specified with `over`.
    Returns:
        Part: The extruded sketch.
    """
    return _plane_from_over_under(over, under, amount) * extrude(sketch, amount)


def make_plate(size: Vec3, fill: Fill | None = None) -> Part:
    """
    Make a plate of the given size and fill pattern.

    Args:
        size (VectorLike): The size of the plate.
        fill (FillPattern, optional): The fill pattern of the plate. Defaults to SOLID.

    Returns:
        Part: The extruded plate.
    """
    sketch = RectangleElement(size.x, size.y, fill=fill).sketch()
    return extrude(sketch, size.z)

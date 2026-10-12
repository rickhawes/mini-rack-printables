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
)
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
    def render(self) -> Part:
        """Extrudes the shape along the z-axis."""
        pass


class PrismElement(Element3D):
    """A prism element."""

    element: Element2D
    amount: Mm

    def __init__(self, element: Element2D, amount: Mm) -> None:
        self.element = element
        self.amount = amount

    @override
    def size(self) -> Vec3:
        size2d = self.element.size()
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def render(self) -> Part:
        return extrude(self.element.sketch())


class BoxElement(PrismElement):
    """A box element."""
    def __init__(self, dx: Mm, dy: Mm, dz: Mm) -> None:
        super().__init__(RectangleElement(dx, dy), dz)


class TubeElement(Element3D):
    """A tube element."""

    element: Element2D
    amount: Mm
    wall_thickness: Mm

    def __init__(self, element: Element2D, amount: Mm, wall_thickness: Mm) -> None:
        self.element = element
        self.amount = amount
        self.wall_thickness = wall_thickness

    @override
    def size(self) -> Vec3:
        size2d = self.element.size()
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def render(self) -> Part:
        return extrude_tube(self.element, amount=self.amount, wall_thickness=self.wall_thickness)


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


def extrude_tube(element: Element2D, wall_thickness: Mm, amount: Mm) -> Part:
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
    sketch = sketch_ring(element, wall_thickness)
    return extrude(sketch, amount)


def extrude_sketch(sketch: Sketch, amount: Mm) -> Part:
    """
    Extrude a sketch along the Z axis.

    Args:
        sketch (Sketch): The sketch to extrude.
        amount (Mm): The amount to extrude the sketch in the Z direction.
    Returns:
        Part: The extruded sketch.
    """
    return extrude(sketch, amount)


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

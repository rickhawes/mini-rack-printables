"""
3D Elements for models and parts. Elements are the primitives that are to form a model.

See Also:
    Elements2d - for the two equivalent
"""

from abc import ABC, abstractmethod
from typing import override

from build123d import Cone, Cylinder, Location, Part, Sketch, extrude, offset

from .corners import Corners
from .elements_2d import Element2D, RectangleElement, RingElement
from .geometry import Degree, Mm, Vec3
from .hole_patterns import HolePattern
from .piece import Piece


class Element3D(ABC):
    """3d shapes that are composable by an `Assembler`"""

    @property
    @abstractmethod
    def size(self) -> Vec3:
        """Returns the size of the shape in 3d."""

    @abstractmethod
    def render(self, cut: bool = False) -> Piece:
        """Extrudes the shape centered on the plane and the z-axis of the plane"""


class PrismElement(Element3D):
    """A prism element is just an extrusion of a 2d shape."""

    element: Element2D
    amount: Mm
    taper: Degree

    def __init__(self, element: Element2D, amount: Mm, taper: Degree = 0) -> None:
        self.element = element
        self.amount = amount
        self.taper = taper

    @property
    @override
    def size(self) -> Vec3:
        size2d = self.element.size
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def render(self, cut: bool = False) -> Piece:
        part = Location((0, 0, -self.amount / 2)) * extrude(
            self.element.sketch(), amount=self.amount, taper=self.taper
        )
        return Piece(part, cut)


class TubeElement(PrismElement):
    def __init__(self, base: Element2D, thickness: Mm, amount: Mm) -> None:
        super().__init__(RingElement(base, thickness), amount)


class BoxElement(PrismElement):
    """A box element is a 3d cuboid"""

    def __init__(self, dx: Mm, dy: Mm, dz: Mm) -> None:
        super().__init__(RectangleElement(dx, dy), dz)


class PlateElement(PrismElement):
    """A extruded RectangleElement"""

    def __init__(
        self,
        width: Mm,
        height: Mm,
        depth: Mm,
        corners: Mm | Corners | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        super().__init__(RectangleElement(width, height, corners, holes), depth)


class CylinderElement(Element3D):
    """A cylinder element."""

    radius: Mm
    height: Mm

    def __init__(self, radius: Mm, height: Mm) -> None:
        self.radius = radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        return Vec3(2 * self.radius, 2 * self.radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        return Piece(Cylinder(self.radius, self.height), cut)


class ConeElement(Element3D):
    """A cone element."""

    base_radius: Mm
    top_radius: Mm
    height: Mm

    def __init__(self, base_radius: Mm, top_radius: Mm, height: Mm) -> None:
        self.base_radius = base_radius
        self.top_radius = top_radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        max_radius = max(self.base_radius, self.top_radius)
        return Vec3(2 * max_radius, 2 * max_radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        part = Location((0, 0, self.height / 2)) * Cone(
            self.base_radius, self.top_radius, self.height
        )
        return Piece(part, cut)


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
    Returns:
        Part: The extruded tube of the basic shape.
    """
    sketch = sketch_ring(element, wall_thickness)
    return Location((0, 0, -amount / 2)) * extrude(sketch, amount)


def extrude_sketch(sketch: Sketch, amount: Mm) -> Part:
    """
    Extrude a sketch along the Z axis.

    Args:
        sketch (Sketch): The sketch to extrude.
        amount (Mm): The amount to extrude the sketch in the Z direction.
    Returns:
        Part: The extruded sketch.
    """
    return Location((0, 0, -amount / 2)) * extrude(sketch, amount)


def make_plate(size: Vec3, holes: HolePattern | None = None) -> Part:
    """
    Make a plate of the given size and fill pattern.

    Args:
        size (VectorLike): The size of the plate.
        holes (HolePattern, optional): The fill pattern of the plate. Defaults to SOLID.

    Returns:
        Part: The extruded plate.
    """
    sketch = RectangleElement(size.x, size.y, holes=holes).sketch()
    return Location((0, 0, -size.z / 2)) * extrude(sketch, size.z)

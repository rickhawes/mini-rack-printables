from .face_selector import select_plane, FaceSelector
from abc import ABC, abstractmethod

from build123d import (
    Rectangle,
    Vector,
    Circle,
    RectangleRounded,
    SlotOverall,
    Sketch,
    extrude,
    offset,
    Part,
    Face,
    Plane,
    Location,
)


#
# A system of 2d  that are used in the parts in the rack.
#
# Dev Note: Create this subset of the features of the build123d library's as a
# set of primatives for the part library that is supported by the package
#
class PrimativeShape(ABC):
    """ABC for the primative shapes that are used for parts in the rack."""

    @abstractmethod
    def size(self) -> Vector:
        """Returns the size of the shape."""
        pass

    @abstractmethod
    def draw(self) -> Sketch:
        """Draw the outline of the shape."""
        pass


class PrimativeCircle(PrimativeShape):
    """A circle shape."""

    def __init__(self, radius: float):
        self.radius = radius

    def size(self) -> Vector:
        return Vector(2 * self.radius, 2 * self.radius)

    def draw(self) -> Sketch:
        return Circle(self.radius)


class PrimativeRectangle(PrimativeShape):
    """A rectangle shape or rounded rectangle shape."""

    def __init__(self, width: float, height: float, radius: float = 0):
        self.width = width
        self.height = height
        self.radius = radius

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def draw(self) -> Sketch:
        if self.radius > 0:
            return RectangleRounded(self.width, self.height, self.radius)
        else:
            return Rectangle(self.width, self.height)


class PrimativeSlot(PrimativeShape):
    """A slot shape."""

    def __init__(self, width: float, height: float):
        self.width = width
        self.height = height

    def size(self) -> Vector:
        return Vector(self.width, self.height)

    def draw(self) -> Sketch:
        return SlotOverall(self.width, self.height)


def _plane_from_over_under(
    over: Part | Face | None, under: Part | Face | None, amount: float
) -> Plane:
    """Helper to get the plane from the on_top_of argument."""
    if over is None and under is None:
        return Plane.XY
    elif isinstance(over, Face) and under is None:
        return Plane(over)
    elif over is None and isinstance(under, Face):
        return Plane(Plane(under) * Location((0, 0, -amount)))
    elif isinstance(over, Part) and under is None:
        return select_plane(over, FaceSelector.MAX_Z)
    elif over is None and isinstance(under, Part):
        return Plane(select_plane(under, FaceSelector.MAX_Z) * Location((0, 0, -amount)))
    else:
        assert False, "Invalid over and under combination"


def make_primative_prism(
    shape: PrimativeShape,
    amount: float,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a basic prism from the primative shape.
    The extrusion is done from the XY plane or the MAX_Z of the on_top_of part.

    Args:
        shape (PrimativeShape): The shape of the prism.
        amount (float): The amount to extrude the prism in the Z direction.
        on_top_of (Part | Face | None, optional): The plane to extrude on top of. Defaults to XY.

    Returns:
        Part: The extruded prism of the basic shape.
    """
    return _plane_from_over_under(over, under, amount) * extrude(shape.draw(), amount)


def make_primative_ring(shape: PrimativeShape, wall_thickness: float) -> Sketch:
    """
    Make a 2d ring from the primative shape.

    Args:
        shape (PrimativeShape): The shape of the ring.
        wall_thickness (float): The thickness of the ring wall.
        on_top_of (Part | Face | None, optional): The plane to extrude on top of. Defaults to XY.

    Returns:
        Part: The extruded ring of the basic shape.
    """
    inner = shape.draw()
    outer = offset(inner, wall_thickness)
    return Sketch(outer - inner)


def make_primative_tube(
    shape: PrimativeShape,
    wall_thickness: float,
    amount: float,
    over: Part | Face | None = None,
    under: Part | Face | None = None,
) -> Part:
    """
    Make a 3d tube from the primative shape by outsetting the shape and extruding it along the Z axis.

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
    sketch = make_primative_ring(shape, wall_thickness)
    return plane * extrude(sketch, amount)

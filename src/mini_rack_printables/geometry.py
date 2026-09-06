from dataclasses import dataclass
import numpy as np
from build123d import Vector, VectorLike, Axis

from .selectors import Place


@dataclass
class Rc:
    """
    Class representing a rectangle in 2d-space. Usefull in laying out features of models.
    """

    size: Vector
    shift: Vector

    def __init__(self, size: VectorLike, shift: VectorLike = Vector(0, 0)):
        self.size = Vector(size)
        self.shift = Vector(shift)

    @classmethod
    def from_edges(cls, left: float, right: float, bottom: float, top: float) -> Rc:
        return Rc(
            size=Vector(right - left, top - bottom),
            shift=Vector((right + left) / 2, (top + bottom) / 2),
        )

    @classmethod
    def union(cls, r1: Rc, r2: Rc) -> Rc:
        return Rc.from_edges(
            right=max(r1.right, r2.right),
            left=min(r1.left, r2.left),
            top=max(r1.top, r2.top),
            bottom=min(r1.bottom, r2.bottom),
        )

    @property
    def left(self) -> float:
        return -self.size.X / 2 + self.shift.X

    @property
    def bottom(self) -> float:
        return -self.size.Y / 2 + self.shift.Y

    @property
    def right(self) -> float:
        return self.size.X / 2 + self.shift.X

    @property
    def top(self) -> float:
        return self.size.Y / 2 + self.shift.Y

    def apply_padding(self, padding: float) -> Rc:
        """
        Apply padding to the Rc, expanding its size by `padding` amount but not shifting its center.
        """
        return Rc(size=self.size + Vector(2 * padding, 2 * padding), shift=self.shift)

    def split(self, amount: float, axis: Axis = Axis.X) -> list[Rc]:
        if axis == Axis.X:
            mid = self.left + amount if amount > 0 else self.right + amount
            return [
                Rc.from_edges(self.left, mid, self.bottom, self.top),
                Rc.from_edges(mid, self.right, self.bottom, self.top),
            ]
        else:
            mid = self.bottom + amount if amount > 0 else self.top + amount
            return [
                Rc.from_edges(self.left, self.right, self.bottom, mid),
                Rc.from_edges(self.left, self.right, mid, self.top),
            ]

    def divide(self, by: int, axis: Axis = Axis.X) -> list[Rc]:
        """
        Divide the rectangle into `by` equal rectangles in `dir` direction.
        """
        if axis == Axis.X:
            dx = self.size.X / by
            size_x = self.size.X
            return [
                Rc(
                    size=Vector(dx, self.size.Y),
                    shift=Vector(self.shift.X + x, self.shift.Y),
                )
                for x in np.linspace((-size_x + dx) / 2, (size_x - dx) / 2, by)
            ]
        else:
            dy = self.size.Y / by
            size_y = self.size.Y
            return [
                Rc(
                    size=Vector(self.size.X, dy),
                    shift=Vector(self.shift.X, self.shift.Y + y),
                )
                for y in np.linspace((-size_y + dy) / 2, (size_y - dy) / 2, by)
            ]

    def place_position(self, place: Place) -> Vector:
        """
        Returns the position (an x, y vector) of the place on the rectangle.
        """
        place_x, place_y = place.as_units()
        return Vector(
            (self.size.X / 2) * place_x + self.shift.X,
            (self.size.Y / 2) * place_y + self.shift.Y,
        )

    def bounded_shift(self, bounds: Rc, align: Place) -> Vector:
        """
        The amount of shift to apply to this Rc to place it within the `bounds` according to
        the `place`. Useful in layout calculations.
        """
        return bounds.place_position(align) - self.place_position(align)

    def alignment_shift(self, other: Rc, align: Alignment) -> Vector:
        """
        The shift to align the `other` rectangle with this one according to the alignment.
        Useful in placement calculations.
        """
        self_pos = self.place_position(align.main)
        other_pos = other.place_position(align.other)
        return self_pos - other_pos

    def centered_bounding(self) -> Rc:
        """
        return a rectangle in opposite direction of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vector(-self.shift.X, -self.shift.Y))
        return Rc.union(self, mirror)


@dataclass(frozen=True)
class Alignment:
    """
    Represents the alignment of two Rcs, or two 2d shapes,
    """

    main: Place
    """The position in the main shape to align with"""

    other: Place
    """The position in the other shape to align with"""


@dataclass(frozen=True)
class Rib:
    """
    Represents a rib (width x depth) on a part or shape
    """

    width: float
    depth: float


def convert_to_3d(vector2d: Vector, z: float = 0) -> Vector:
    """
    Convert a 2D vector to a 3D vector with Z=0
    """
    return Vector(vector2d.X, vector2d.Y, z)

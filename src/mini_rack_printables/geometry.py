from build123d import Vector, VectorLike
from dataclasses import dataclass
import numpy as np
from enum import Enum
from math import floor


class AlignmentVector(Vector, Enum):
    """
    Enum for aligning an Rc
    """

    CENTER = Vector(0, 0, 0)
    LEFT = Vector(-1, 0, 0)
    RIGHT = Vector(1, 0, 0)
    TOP = Vector(0, 1, 0)
    BOTTOM = Vector(0, -1, 0)
    FRONT = Vector(0, 0, 1)
    BACK = Vector(0, 0, -1)

    @classmethod
    def is_valid(cls, vec: Vector) -> bool:
        return (
            (vec.X == 1.0 or vec.X == 0 or vec.X == -1.0)
            and (vec.Y == 1.0 or vec.Y == 0 or vec.Y == -1.0)
            and (vec.Z == 1.0 or vec.Z == 0 or vec.Z == -1.0)
        )


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
        return Rc.from_edges(
            right=self.right + padding,
            left=self.left - padding,
            top=self.top + padding,
            bottom=self.bottom - padding,
        )

    def split(self, dx: float = 0, dy: float = 0.0) -> list[Rc]:
        assert not (dx != 0 and dy != 0), "must only have one of dx or dy"
        assert not (dx == 0 and dy == 0), "must specify either dx or dy"
        if dx > 0:
            return [
                Rc.from_edges(
                    left=self.left,
                    right=self.left + dx,
                    bottom=self.bottom,
                    top=self.top,
                ),
                Rc.from_edges(
                    left=self.left + dx,
                    right=self.right,
                    bottom=self.bottom,
                    top=self.top,
                ),
            ]
        elif dx < 0:
            return [
                Rc.from_edges(
                    left=self.left,
                    right=self.right + dx,
                    bottom=self.bottom,
                    top=self.top,
                ),
                Rc.from_edges(
                    left=self.right + dx,
                    right=self.right,
                    bottom=self.bottom,
                    top=self.top,
                ),
            ]
        elif dy > 0:
            return [
                Rc.from_edges(
                    left=self.left,
                    right=self.right,
                    bottom=self.bottom,
                    top=self.bottom + dy,
                ),
                Rc.from_edges(
                    left=self.left,
                    right=self.right,
                    bottom=self.bottom + dy,
                    top=self.top,
                ),
            ]
        else:
            assert dy < 0
            return [
                Rc.from_edges(
                    left=self.left,
                    right=self.right,
                    bottom=self.bottom,
                    top=self.top + dy,
                ),
                Rc.from_edges(
                    left=self.left, right=self.right, bottom=self.top + dy, top=self.top
                ),
            ]

    def divide_horizontally(self, by: int) -> list[Rc]:
        division_dx = self.size.X / by
        return [
            Rc(
                size=Vector(division_dx, self.size.Y),
                shift=Vector(self.shift.X + x, self.shift.Y),
            )
            for x in np.linspace((-self.size.X+division_dx)/2, (self.size.X-division_dx)/2, by)
        ]

    def divide_vertically(self, by: int) -> list[Rc]:
        division_dy = self.size.Y / by
        return [
            Rc(
                size=Vector(self.size.X, division_dy),
                shift=Vector(self.shift.X, self.shift.Y + y),
            )
            for y in np.linspace((-self.size.Y+division_dy)/2, (self.size.Y-division_dy)/2, by)
        ]

    def alignment_shift(self, bounds: Rc, align: Vector) -> Vector:
        """
        return the amount of shift to align within the bounds according the alignment vector
        """
        assert AlignmentVector.is_valid(align), "must be an alignment vector value"
        return Vector(
            (bounds.size.X - self.size.X) * align.X / 2 + bounds.shift.X,
            (bounds.size.Y - self.size.Y) * align.Y / 2 + bounds.shift.Y,
        )

    def align(self, bounds: Rc, align: Vector) -> Rc:
        """
        Return an Rc that has been shifted to match alignment the bounds and alignment vector
        """
        return Rc(size=self.size, shift=self.alignment_shift(bounds, align))

    def centered_bounding(self) -> Rc:
        """
        return a rectangle in opposite direction of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vector(-self.shift.X, -self.shift.Y))
        return Rc.union(self, mirror)

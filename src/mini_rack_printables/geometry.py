from dataclasses import dataclass
import numpy as np
from typing import Self
from build123d import Vector, VectorLike, Axis, Align

from .selectors import Place, place_from_aligns


@dataclass(frozen=True, init=False)
class Bx:
    """
    Represents a axis aligned 3d box.
    """

    size: Vector
    shift: Vector

    def __init__(self, size: VectorLike, shift: VectorLike = Vector(0, 0, 0)):
        sz = Vector(size)
        sh = Vector(shift)
        object.__setattr__(self, "size", sz)
        object.__setattr__(self, "shift", sh)

    @classmethod
    def from_edges(
        cls,
        left: float,
        right: float,
        bottom: float,
        top: float,
        front: float = 0,
        back: float = 0,
    ) -> Self:
        return cls(
            size=Vector(right - left, top - bottom, back - front),
            shift=Vector((right + left) / 2, (top + bottom) / 2, (back + front) / 2),
        )

    @classmethod
    def union(cls, r1: Rc, r2: Rc) -> Self:
        return cls.from_edges(
            right=max(r1.right, r2.right),
            left=min(r1.left, r2.left),
            top=max(r1.top, r2.top),
            bottom=min(r1.bottom, r2.bottom),
            front=min(r1.front, r2.front),
            back=max(r1.back, r2.back),
        )

    @property
    def min(self) -> Vector:
        return self.shift - 0.5 * self.size

    @property
    def max(self) -> Vector:
        return self.shift + 0.5 * self.size

    @property
    def top(self) -> float:
        return self.max.Y

    @property
    def bottom(self) -> float:
        return self.min.Y

    @property
    def left(self) -> float:
        return self.min.X

    @property
    def right(self) -> float:
        return self.max.X

    @property
    def front(self) -> float:
        return self.min.Z

    @property
    def back(self) -> float:
        return self.max.Z

    def shifted(self, shift: VectorLike) -> Self:
        return self.__class__(size=self.size, shift=Vector(shift))

    def shifted_by(self, shift: VectorLike) -> Self:
        return self.shifted(self.shift + Vector(shift))


@dataclass(frozen=True, init=False)
class Rc(Bx):
    """
    Class representing a rectangle in 2d-space which is a special case of 3d Bx.
    Useful in laying out features of models.
    """

    def __init__(self, size: VectorLike, shift: VectorLike = Vector(0, 0)):
        sz = Vector(size)
        sz.Z = 0
        sh = Vector(shift)
        sh.Z = 0
        super().__init__(sz, sh)

    def anchor_shifted(self, anchor: Place | tuple[Align, Align]) -> Rc:
        """
        Return a new Rc with the same size but
        shifted so that the anchor's position is at the rectangle's center
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return Rc(size=self.size, shift=self.anchor_position(anchor))

    def anchor_position(self, anchor: Place | tuple[Align, Align]) -> Vector:
        """
        Returns the position (an x, y vector) of the 'anchor' on the rectangle.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        place_x, place_y = anchor.as_units()
        return Vector(
            (self.size.X / 2) * place_x + self.shift.X,
            (self.size.Y / 2) * place_y + self.shift.Y,
        )

    def bounds_shifted(self, bounds: Rc, anchor: Place | tuple[Align, Align]) -> Rc:
        """
        Return a new Rc with the same size but shifted so that `align` is at the origin.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return Rc(size=self.size, shift=self.bounds_shift(bounds, anchor))

    def bounds_shift(self, bounds: Rc, anchor: Place | tuple[Align, Align]) -> Vector:
        """
        The amount of shift to apply to this Rc to place it within the `bounds` according to
        the `place`. Useful in layout calculations.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return bounds.anchor_position(anchor) - self.anchor_position(anchor)

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

    def divide_evenly(self, by: int, axis: Axis = Axis.X) -> list[Rc]:
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

    def centered_bounding(self) -> Rc:
        """
        return a rectangle in opposite direction of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vector(-self.shift.X, -self.shift.Y))
        return Rc.union(self, mirror)

    def form_bx(self, front: float, back: float) -> Bx:
        return Bx(
            size=Vector(self.size.X, self.size.Y, back - front),
            shift=Vector(self.shift.X, self.shift.Y, (back + front) / 2),
        )

    @staticmethod
    def arrange(
        axis: Axis,
        align: Place | tuple[Align, Align],
        *items: Rc,
    ) -> list[Rc]:
        """
        Arrange a collection of Rcs along an axis, aligning the collection according to the given alignment.

        Args:
            axis (Axis): The axis to arrange along.
            anchor (tuple[Align, Align]): The origin point for the whole collection.
            *items (Rc): The Rcs to arrange.

        Returns:
            list[Rc]: The arranged Rcs.
        """
        if len(items) == 0:
            return []
        if isinstance(align, tuple):
            align = place_from_aligns(align)
        if axis == Axis.X:
            if align not in (Place.CENTER, Place.BOTTOM, Place.TOP):
                raise ValueError(f"Invalid align for axis X: {align}")
            bounds = Rc(
                size=(sum(item.size.X for item in items), max(item.size.Y for item in items))
            )
            edge = bounds.left
            output: list[Rc] = []
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.X, bounds.bottom, bounds.top)
                arranged_item = item.bounds_shifted(item_bounds, align)
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        else:
            if align not in (Place.CENTER, Place.LEFT, Place.RIGHT):
                raise ValueError(f"Invalid align for axis Y: {align}")
            bounds = Rc(
                size=(max(item.size.X for item in items), sum(item.size.Y for item in items))
            )
            edge = bounds.bottom
            output: list[Rc] = []
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.Y)
                arranged_item = item.bounds_shifted(item_bounds, align)
                output.append(arranged_item)
                edge = item_bounds.top
            return output


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

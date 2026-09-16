from dataclasses import dataclass
import numpy as np
from build123d import Vector, VectorLike, Axis, Align

from .selectors import Place, place_from_aligns


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

    def shifted(self, shift: Vector) -> Rc:
        """
        Return a new Rc with the same size but shifted by `shift`.
        """
        return Rc(size=self.size, shift=shift)

    def resized(self, size: Vector) -> Rc:
        """
        Return a new Rc with the same shift but resized to `size`.
        """
        return Rc(size=size, shift=self.shift)

    def anchor_shifted(self, anchor: Place | tuple[Align, Align]) -> Rc:
        """
        Return a new Rc with the same size but shifted so that `anchor` is at the origin.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return Rc(size=self.size, shift=-self.anchor_position(anchor))

    def anchor_position(self, anchor: Place | tuple[Align, Align]) -> Vector:
        """
        Returns the position (an x, y vector) of the place on the rectangle.
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

    @staticmethod
    def arrange(
        axis: Axis,
        anchor: Place | tuple[Align, Align],
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
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        if axis == Axis.X:
            bounds = Rc(
                size=(sum(item.size.X for item in items), max(item.size.Y for item in items))
            ).anchor_shifted(anchor)
            edge = bounds.left
            output: list[Rc] = []
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.X, bounds.bottom, bounds.top)
                arranged_item = item.bounds_shifted(item_bounds, anchor)
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        else:
            bounds = Rc(
                size=(max(item.size.X for item in items), sum(item.size.Y for item in items))
            ).anchor_shifted(anchor)
            edge = bounds.bottom
            output: list[Rc] = []
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.Y)
                arranged_item = item.bounds_shifted(item_bounds, anchor)
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

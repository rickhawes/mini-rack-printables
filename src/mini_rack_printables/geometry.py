"""
Structures and functions for computing the geometry of rectangles and boxes.
"""

from dataclasses import dataclass
import numpy as np
from typing import Self, overload
from build123d import Axis, Align, Vector

from .selectors import Place, place_from_aligns


@dataclass(frozen=True)
class Vec3:
    """
    3D-space vector
    """

    x: float
    y: float
    z: float

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: float) -> Self:
        return self.__class__(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: float) -> Self:
        return self.__class__(self.x / other, self.y / other, self.z / other)

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y, -self.z)

    def __repr__(self) -> str:
        return f"Vec3({self.x}, {self.y}, {self.z})"

    def to_2d(self) -> Vec2:
        return Vec2(self.x, self.y)

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y, self.z)

    def to_tuple(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass(frozen=True)
class Vec2:
    """
    2d space vector
    """

    x: float
    y: float

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, other: float) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __truediv__(self, other: float) -> Self:
        return self.__class__(self.x / other, self.y / other)

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y)

    def __repr__(self) -> str:
        return f"Vec2({self.x}, {self.y})"

    def to_3d(self, z: float = 0) -> Vec3:
        return Vec3(self.x, self.y, z)

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y)

    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass(frozen=True, init=False)
class Bx:
    """
    Represents an axis aligned 3d box.
    """

    size: Vec3
    shift: Vec3

    @overload
    def __init__(self, other: Bx) -> None: ...
    @overload
    def __init__(self, size: Vec3) -> None: ...
    @overload
    def __init__(self, size: Vec3, shift: Vec3) -> None: ...
    @overload
    def __init__(self, dx: float, dy: float, dz: float) -> None: ...
    @overload
    def __init__(self, dx: float, dy: float, dz: float, x: float, y: float, z: float) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        """
        Args:
            other: Another Bx
            size: The size of the box.
            shift: The shift of the box. Default (0,0,0)
            dx: The x dimension of the box.
            dy: The y dimension of the box.
            dz: The z dimension of the box.
            x: The x shift of the box. Default 0.
            y: The y shift of the box. Default 0.
            z: The z shift of the box. Default 0.
        """
        # Size and shift
        if "size" in kwargs:
            size = kwargs["size"]
            shift = kwargs.get("shift", Vec3(0, 0, 0))
            if not isinstance(size, Vec3) or not isinstance(shift, Vec3):
                raise TypeError("size and shift must be a Vec3")
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        # Size from dx/dy/dz and shift from x/y/z
        if "dx" in kwargs and "dy" in kwargs and "dz" in kwargs:

            def get_float(name: str, default: float | None = None) -> float:
                v = kwargs.get(name)
                if v is None and default is None:
                    raise ValueError(f"{name} must be supplied")
                elif v is None and default is not None:
                    v = default
                elif not isinstance(v, (int, float)):
                    raise TypeError(f"{name} must be a float")
                return v

            dx, dy, dz = get_float("dx"), get_float("dy"), get_float("dz")
            x, y, z = get_float("x", 0), get_float("y", 0), get_float("z", 0)
            object.__setattr__(self, "size", Vec3(dx, dy, dz))
            object.__setattr__(self, "shift", Vec3(x, y, z))
            return

        # Other
        if "other" in kwargs:
            other = kwargs["other"]
            if not isinstance(other, Bx):
                raise TypeError("other must be a Bx")
            object.__setattr__(self, "size", other.size)
            object.__setattr__(self, "shift", other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Bx):
            other = args[0]
            object.__setattr__(self, "size", other.size)
            object.__setattr__(self, "shift", other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Vec3):
            size = args[0]
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", Vec3(0, 0, 0))
            return

        if len(args) == 2 and isinstance(args[0], Vec3) and isinstance(args[1], Vec3):
            size = args[0]
            shift = args[1]
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        if (
            len(args) == 3
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
            and isinstance(args[2], (int, float))
        ):
            size = Vec3(args[0], args[1], args[2])
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", Vec3(0, 0, 0))
            return

        if (
            len(args) == 6
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
            and isinstance(args[2], (int, float))
        ):
            size = Vec3(args[0], args[1], args[2])
            shift = Vec3(args[3], args[4], args[5])
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        raise ValueError(f"Init error with parameters {[*args]}")

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
            size=Vec3(right - left, top - bottom, back - front),
            shift=Vec3((right + left) / 2, (top + bottom) / 2, (back + front) / 2),
        )

    @classmethod
    def union(cls, r1: Bx, r2: Bx) -> Self:
        return cls.from_edges(
            right=max(r1.right, r2.right),
            left=min(r1.left, r2.left),
            top=max(r1.top, r2.top),
            bottom=min(r1.bottom, r2.bottom),
            front=min(r1.front, r2.front),
            back=max(r1.back, r2.back),
        )

    @property
    def min(self) -> Vec3:
        return self.shift - (self.size / 2)

    @property
    def max(self) -> Vec3:
        return self.shift + (self.size / 2)

    @property
    def top(self) -> float:
        return self.max.y

    @property
    def bottom(self) -> float:
        return self.min.y

    @property
    def left(self) -> float:
        return self.min.x

    @property
    def right(self) -> float:
        return self.max.x

    @property
    def front(self) -> float:
        return self.min.z

    @property
    def back(self) -> float:
        return self.max.z

    def shifted(self, shift: Vec3) -> Self:
        return self.__class__(size=self.size, shift=shift)

    def shifted_by(self, shift: Vec3) -> Self:
        return self.shifted(self.shift + shift)


@dataclass(frozen=True, init=False)
class Rc:
    """
    Class representing a XY axis aligned rectangle in 2d-space.
    """

    size: Vec2
    shift: Vec2

    @overload
    def __init__(self, other: Rc) -> None: ...
    @overload
    def __init__(self, size: Vec2, shift: Vec2) -> None: ...
    @overload
    def __init__(self, size: Vec2) -> None: ...
    @overload
    def __init__(self, dx: float, dy: float, x: float, y: float) -> None: ...
    @overload
    def __init__(self, dx: float, dy: float) -> None: ...

    def __init__(self, *args, **kwargs) -> None:
        """
        Args:
            other: Another Rc
            size: The size of the box.
            shift: The shift of the box. Default (0,0)
            dx: The x dimension of the box.
            dy: The y dimension of the box.
            x: The x shift of the box. Default 0.
            y: The y shift of the box. Default 0.
        """
        # Size and shift
        if "size" in kwargs:
            size = kwargs["size"]
            shift = kwargs.get("shift", Vec2(0, 0))
            if not isinstance(size, Vec2) or not isinstance(shift, Vec2):
                raise TypeError("size and shift must be a Vec3")
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        # Size from dx/dy/dz and shift from x/y/z
        if "dx" in kwargs and "dy" in kwargs and "dz" in kwargs:

            def get_float(name: str, default: float | None = None) -> float:
                v = kwargs.get(name)
                if v is None and default is None:
                    raise ValueError(f"{name} must be supplied")
                elif v is None and default is not None:
                    v = default
                elif not isinstance(v, (int, float)):
                    raise TypeError(f"{name} must be a float")
                return v

            dx, dy = get_float("dx"), get_float("dy")
            x, y = get_float("x", 0), get_float("y", 0)
            object.__setattr__(self, "size", Vec2(dx, dy))
            object.__setattr__(self, "shift", Vec2(x, y))
            return

        # Other
        if "other" in kwargs:
            other = kwargs["other"]
            if not isinstance(other, Rc):
                raise TypeError("other must be a Rc")
            object.__setattr__(self, "size", other.size)
            object.__setattr__(self, "shift", other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Rc):
            other = args[0]
            object.__setattr__(self, "size", other.size)
            object.__setattr__(self, "shift", other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Vec2):
            size = args[0]
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", Vec2(0, 0))
            return

        if len(args) == 2 and isinstance(args[0], Vec2) and isinstance(args[1], Vec2):
            size = args[0]
            shift = args[1]
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        if (
            len(args) == 2
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
        ):
            size = Vec2(args[0], args[1])
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", Vec2(0, 0))
            return

        if (
            len(args) == 4
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
        ):
            size = Vec2(args[0], args[1])
            shift = Vec2(args[2], args[3])
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)
            return

        raise ValueError(f"Init error with parameters {[*args]}")

    @classmethod
    def from_edges(
        cls,
        left: float,
        right: float,
        bottom: float,
        top: float,
    ) -> Self:
        return cls(
            size=Vec2(right - left, top - bottom),
            shift=Vec2((right + left) / 2, (top + bottom) / 2),
        )

    @classmethod
    def union(cls, r1: Rc, r2: Rc) -> Self:
        return cls.from_edges(
            right=max(r1.right, r2.right),
            left=min(r1.left, r2.left),
            top=max(r1.top, r2.top),
            bottom=min(r1.bottom, r2.bottom),
        )

    @property
    def min(self) -> Vec2:
        return self.shift - (self.size / 2)

    @property
    def max(self) -> Vec2:
        return self.shift + (self.size / 2)

    @property
    def top(self) -> float:
        return self.max.y

    @property
    def bottom(self) -> float:
        return self.min.y

    @property
    def left(self) -> float:
        return self.min.x

    @property
    def right(self) -> float:
        return self.max.x

    def shifted(self, shift: Vec2) -> Self:
        return self.__class__(size=self.size, shift=shift)

    def shifted_by(self, shift: Vec2) -> Self:
        return self.shifted(self.shift + shift)

    def anchor_shifted(self, anchor: Place | tuple[Align, Align]) -> Rc:
        """
        Return a new Rc with the same size but
        shifted so that the anchor's position is at the rectangle's center
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return Rc(size=self.size, shift=self.anchor_position(anchor))

    def anchor_position(self, anchor: Place | tuple[Align, Align]) -> Vec2:
        """
        Returns the position (an x, y vector) of the 'anchor' on the rectangle.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        place_x, place_y = anchor.as_units()
        return Vec2(
            (self.size.x / 2) * place_x + self.shift.x,
            (self.size.y / 2) * place_y + self.shift.y,
        )

    def bounds_shifted(self, bounds: Rc, anchor: Place | tuple[Align, Align]) -> Rc:
        """
        Return a new Rc with the same size but shifted so that `align` is at the origin.
        """
        if isinstance(anchor, tuple):
            anchor = place_from_aligns(anchor)
        return Rc(size=self.size, shift=self.bounds_shift(bounds, anchor))

    def bounds_shift(self, bounds: Rc, anchor: Place | tuple[Align, Align]) -> Vec2:
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
        return Rc(size=self.size + Vec2(2 * padding, 2 * padding), shift=self.shift)

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
            dx = self.size.x / by
            size_x = self.size.x
            return [
                Rc(
                    size=Vec2(dx, self.size.y),
                    shift=Vec2(self.shift.x + x, self.shift.y),
                )
                for x in np.linspace((-size_x + dx) / 2, (size_x - dx) / 2, by)
            ]
        else:
            dy = self.size.y / by
            size_y = self.size.y
            return [
                Rc(
                    size=Vec2(self.size.x, dy),
                    shift=Vec2(self.shift.x, self.shift.y + y),
                )
                for y in np.linspace((-size_y + dy) / 2, (size_y - dy) / 2, by)
            ]

    def centered_bounding(self) -> Rc:
        """
        return a rectangle in opposite direction of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vec2(-self.shift.x, -self.shift.y))
        return Rc.union(self, mirror)

    def form_bx(self, front: float, back: float) -> Bx:
        return Bx(
            size=Vec3(self.size.x, self.size.y, back - front),
            shift=Vec3(self.shift.x, self.shift.y, (back + front) / 2),
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
        output: list[Rc] = []
        if len(items) == 0:
            return []
        if isinstance(align, tuple):
            align = place_from_aligns(align)
        if axis == Axis.X:
            if align not in (Place.CENTER, Place.BOTTOM, Place.TOP):
                raise ValueError(f"Invalid align for axis X: {align}")
            bounds = Rc(sum(item.size.x for item in items), max(item.size.y for item in items))
            edge = bounds.left
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.x, bounds.bottom, bounds.top)
                arranged_item = item.bounds_shifted(item_bounds, align)
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        else:
            if align not in (Place.CENTER, Place.LEFT, Place.RIGHT):
                raise ValueError(f"Invalid align for axis Y: {align}")
            bounds = Rc(max(item.size.x for item in items), sum(item.size.y for item in items))
            edge = bounds.bottom
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.y)
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

"""
Structures and functions for computing the geometry of rectangles and boxes.
"""

from dataclasses import dataclass
from typing import Self, overload
from build123d import Vector

from .selectors import Place, Ax


type Mm = float | int
"""
A millimeter measurement value
"""


@dataclass(frozen=True)
class Vec3:
    """
    3D-space vector
    """

    x: Mm
    """x value"""
    y: Mm
    """y value"""
    z: Mm
    """z value"""

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: Mm) -> Self:
        return self.__class__(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: Mm) -> Self:
        return self.__class__(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other: Mm) -> Self:
        return self.__class__(self.x / other, self.y / other, self.z / other)

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y, -self.z)

    def to_2d(self) -> Vec2:
        return Vec2(self.x, self.y)

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y, self.z)

    def to_tuple(self) -> tuple[Mm, Mm, Mm]:
        return self.x, self.y, self.z


@dataclass(frozen=True)
class Vec2:
    """
    2d space vector
    """

    x: Mm
    """x value"""
    y: Mm
    """y value"""

    def __add__(self, other: Self) -> Self:
        return self.__class__(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Self) -> Self:
        return self.__class__(self.x - other.x, self.y - other.y)

    def __mul__(self, other: Mm) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __rmul__(self, other: Mm) -> Self:
        return self.__class__(self.x * other, self.y * other)

    def __truediv__(self, other: Mm) -> Self:
        return self.__class__(self.x / other, self.y / other)

    def __neg__(self) -> Self:
        return self.__class__(-self.x, -self.y)

    def to_3d(self, z: Mm = 0) -> Vec3:
        return Vec3(self.x, self.y, z)

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y)

    def to_tuple(self) -> tuple[Mm, Mm]:
        return self.x, self.y


@dataclass(frozen=True, init=False)
class Bx:
    """
    Represents an axis aligned 3d box.
    """

    size: Vec3
    """Size of the box"""
    shift: Vec3
    """Center of the box"""

    @overload
    def __init__(self, other: Bx) -> None: ...
    @overload
    def __init__(self, size: Vec3) -> None: ...
    @overload
    def __init__(self, size: Vec3, shift: Vec3) -> None: ...
    @overload
    def __init__(self, dx: Mm, dy: Mm, dz: Mm) -> None: ...
    @overload
    def __init__(
        self,
        dx: Mm,
        dy: Mm,
        dz: Mm,
        x: Mm,
        y: Mm,
        z: Mm,
    ) -> None: ...

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

        def set(size: Vec3, shift: Vec3) -> None:
            if size.x < 0 or size.y < 0 or size.z < 0:
                raise ValueError("Size must be positive")
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)

        # Size and shift
        if "size" in kwargs:
            size = kwargs["size"]
            shift = kwargs.get("shift", Vec3(0, 0, 0))
            if not isinstance(size, Vec3) or not isinstance(shift, Vec3):
                raise TypeError("size and shift must be a Vec3")
            set(size, shift)
            return

        # Size from dx/dy/dz and shift from x/y/z
        if "dx" in kwargs and "dy" in kwargs and "dz" in kwargs:

            def get_value(name: str, default: Mm | None = None) -> Mm:
                v = kwargs.get(name, None)
                if v is None and default is None:
                    raise ValueError(f"{name} must be supplied")
                elif v is None and default is not None:
                    v = default
                if isinstance(v, (int, float)):
                    return v
                else:
                    raise TypeError(f"{name} must be supplied")

            dx, dy, dz = get_value("dx"), get_value("dy"), get_value("dz")
            x, y, z = get_value("x", 0), get_value("y", 0), get_value("z", 0)
            set(Vec3(dx, dy, dz), Vec3(x, y, z))
            return

        # Other
        if "other" in kwargs:
            other = kwargs["other"]
            if not isinstance(other, Bx):
                raise TypeError("other must be a Bx")
            set(other.size, other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Bx):
            other = args[0]
            set(other.size, other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Vec3):
            size = args[0]
            set(size, Vec3(0, 0, 0))
            return

        if len(args) == 2 and isinstance(args[0], Vec3) and isinstance(args[1], Vec3):
            size = args[0]
            shift = args[1]
            set(size, shift)
            return

        if (
            len(args) == 3
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
            and isinstance(args[2], (int, float))
        ):
            size = Vec3(args[0], args[1], args[2])
            set(size, Vec3(0, 0, 0))
            return

        if (
            len(args) == 6
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
            and isinstance(args[2], (int, float))
        ):
            size = Vec3(args[0], args[1], args[2])
            shift = Vec3(args[3], args[4], args[5])
            set(size, shift)
            return

        raise ValueError(f"Missing parameters {[*args], [*kwargs]}")

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
    def top(self) -> Mm:
        return self.max.y

    @property
    def bottom(self) -> Mm:
        return self.min.y

    @property
    def left(self) -> Mm:
        return self.min.x

    @property
    def right(self) -> Mm:
        return self.max.x

    @property
    def front(self) -> Mm:
        return self.min.z

    @property
    def back(self) -> Mm:
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
    """Size of the rectangle"""
    shift: Vec2
    """The center of the rectangle"""

    @overload
    def __init__(self, other: Rc) -> None: ...
    @overload
    def __init__(self, size: Vec2, shift: Vec2) -> None: ...
    @overload
    def __init__(self, size: Vec2) -> None: ...
    @overload
    def __init__(self, dx: Mm, dy: Mm, x: Mm, y: Mm) -> None: ...
    @overload
    def __init__(self, dx: Mm, dy: Mm) -> None: ...

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

        def set(size: Vec2, shift: Vec2) -> None:
            if size.x < 0 or size.y < 0:
                raise ValueError("Size must be positive")
            object.__setattr__(self, "size", size)
            object.__setattr__(self, "shift", shift)

        # Size and shift
        if "size" in kwargs:
            size = kwargs["size"]
            shift = kwargs.get("shift", Vec2(0, 0))
            if not isinstance(size, Vec2) or not isinstance(shift, Vec2):
                raise TypeError("size and shift must be a Vec3")
            set(size, shift)
            return

        # Size from dx/dy/dz and shift from x/y/z
        if "dx" in kwargs and "dy" in kwargs:

            def get_value(name: str, default: Mm | None = None) -> float:
                v = kwargs.get(name)
                if v is None and default is None:
                    raise ValueError(f"{name} must be supplied")
                elif v is None and default is not None:
                    v = default
                elif not isinstance(v, (int, float)):
                    raise TypeError(f"{name} must be a float")
                return v

            dx, dy = get_value("dx"), get_value("dy")
            x, y = get_value("x", 0), get_value("y", 0)
            set(Vec2(dx, dy), Vec2(x, y))
            return

        # Other
        if "other" in kwargs:
            other = kwargs["other"]
            if not isinstance(other, Rc):
                raise TypeError("other must be a Rc")
            set(other.size, other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Rc):
            other = args[0]
            set(other.size, other.shift)
            return

        if len(args) == 1 and isinstance(args[0], Vec2):
            size = args[0]
            set(size, Vec2(0, 0))
            return

        if len(args) == 2 and isinstance(args[0], Vec2) and isinstance(args[1], Vec2):
            size = args[0]
            shift = args[1]
            set(size, shift)
            return

        if (
            len(args) == 2
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
        ):
            size = Vec2(args[0], args[1])
            set(size, Vec2(0, 0))
            return

        if (
            len(args) == 4
            and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float))
        ):
            size = Vec2(args[0], args[1])
            shift = Vec2(args[2], args[3])
            set(size, shift)
            return

        raise ValueError(f"Missing parameters {[*args], [*kwargs]}")

    @classmethod
    def from_edges(cls, left: Mm, right: Mm, bottom: Mm, top: Mm) -> Self:
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
    def top(self) -> Mm:
        return self.max.y

    @property
    def bottom(self) -> Mm:
        return self.min.y

    @property
    def left(self) -> Mm:
        return self.min.x

    @property
    def right(self) -> Mm:
        return self.max.x

    def shifted(self, shift: Vec2) -> Self:
        return self.__class__(size=self.size, shift=shift)

    def shifted_by(self, shift: Vec2) -> Self:
        return self.shifted(self.shift + shift)

    def anchor_shifted(self, anchor: Place) -> Rc:
        """
        Return a new Rc with the same size but
        shifted so that the anchor's position is at the rectangle's center
        """
        return Rc(size=self.size, shift=self.anchor_position(anchor))

    def anchor_position(self, anchor: Place) -> Vec2:
        """
        Returns the position (an x, y vector) of the 'anchor' on the rectangle.
        """
        place_x, place_y = anchor.as_units()
        return Vec2(
            (self.size.x / 2) * place_x + self.shift.x,
            (self.size.y / 2) * place_y + self.shift.y,
        )

    def bounds_shifted(self, bounds: Rc, anchor: Place) -> Rc:
        """
        Return a new Rc with the same size but shifted so that `align` is at the origin.
        """
        return Rc(size=self.size, shift=self.bounds_shift(bounds, anchor))

    def bounds_shift(self, bounds: Rc, anchor: Place) -> Vec2:
        """
        The amount of shift to apply to this Rc to place it within the `bounds` according to
        the `place`. Useful in layout calculations.
        """
        return bounds.anchor_position(anchor) - self.anchor_position(anchor)

    def apply_padding(self, padding: Mm) -> Rc:
        """
        Apply padding to the Rc, expanding its size by `padding` amount but not shifting its center.
        """
        return Rc(size=self.size + Vec2(2 * padding, 2 * padding), shift=self.shift)

    def split(self, amount: Mm, along: Ax = Ax.X) -> list[Rc]:
        if along == Ax.X:
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

    def centered_bounding(self) -> Rc:
        """
        return a rectangle in opposite direction of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vec2(-self.shift.x, -self.shift.y))
        return Rc.union(self, mirror)

    def form_bx(self, front: Mm, back: Mm) -> Bx:
        return Bx(
            size=Vec3(self.size.x, self.size.y, back - front),
            shift=Vec3(self.shift.x, self.shift.y, (back + front) / 2),
        )

    @staticmethod
    def arrange(
        axis: Ax,
        align: Place,
        *items: Rc,
    ) -> list[Rc]:
        """
        Arrange a collection of Rcs along an axis, aligning the collection according to the given alignment.

        Args:
            axis (Ax): The axis to arrange along.
            align (Place): The edge to align to
            *items (Rc): The Rc list to arrange.

        Returns:
            list[Rc]: The arranged Rcs.
        """
        output: list[Rc] = []
        if len(items) == 0:
            return []
        if axis == Ax.X:
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
        elif axis == Ax.Y:
            if align not in (Place.CENTER, Place.LEFT, Place.RIGHT):
                raise ValueError(f"Invalid place for axis Y: {align}")
            bounds = Rc(max(item.size.x for item in items), sum(item.size.y for item in items))
            edge = bounds.bottom
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.y)
                arranged_item = item.bounds_shifted(item_bounds, align)
                output.append(arranged_item)
                edge = item_bounds.top
            return output
        else:
            raise ValueError(f"Invalid value for axis: {axis}")


@dataclass(frozen=True)
class Rib:
    """
    Represents a rib (width x depth) on a part or shape
    """

    width: Mm
    depth: Mm

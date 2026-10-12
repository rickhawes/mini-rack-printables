"""Classes to specify box and rectangle dimensions and positions.

Used to specify the geometry and bounds of the model.

See Also:
    Placement - Enums to position and align boxes and rectangles
    Element2D, Element3D - Main user of geometry

"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal, Self
from build123d import Vector, Plane

type Mm = float | int
"""A millimeter measurement value. Used for all length measurements in the library."""


class Ax(Enum):
    """Axis placing or align objects.

    Dev Note:
        Ax type is distinguished from the build123d Axis type
    """

    X = auto()
    """ X axis """
    Y = auto()
    """ Y axis """
    Z = auto()
    """ Z axis """


class AxDir(Enum):
    """Enum for the 6 axis aligned AxDirs from the 0,0,0 origin.

    Useful to specify the AxDir of a stack, or the side of the box, or the z-dir of a `Plane`
    The default X-Y Plane has a z-axis AxDir of AxDir.PLUS_Z.
    """

    MINUS_X = auto()
    MINUS_Y = auto()
    MINUS_Z = auto()
    PLUS_X = auto()
    PLUS_Y = auto()
    PLUS_Z = auto()

    # Colloquial names for AxDir
    LEFT = MINUS_X
    RIGHT = PLUS_X
    BOTTOM = MINUS_Y
    TOP = PLUS_Y
    FRONT = MINUS_Z
    BACK = PLUS_Z


class Place(Enum):
    """Place on a rectangle, if the rectangle was divided into 9 regions.

    Useful for specifying the alignment rectangles and elements with each other.
    """

    # Edge of the square
    RIGHT_EDGE = auto()
    LEFT_EDGE = auto()
    TOP_EDGE = auto()
    BOTTOM_EDGE = auto()

    # Corners of a square
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()

    # Center of the square
    CENTER = auto()

    # Aliases for min/max axis values
    MIN_X = LEFT_EDGE
    MIN_Y = BOTTOM_EDGE
    MAX_X = RIGHT_EDGE
    MAX_Y = TOP_EDGE
    NONE = CENTER

    def opposite(self) -> Place:
        """
        Returns the opposite place reflected through the center.
        """
        conversion = {
            Place.RIGHT_EDGE: Place.LEFT_EDGE,
            Place.LEFT_EDGE: Place.RIGHT_EDGE,
            Place.TOP_EDGE: Place.BOTTOM_EDGE,
            Place.BOTTOM_EDGE: Place.TOP_EDGE,
            Place.TOP_RIGHT: Place.BOTTOM_LEFT,
            Place.BOTTOM_RIGHT: Place.TOP_LEFT,
            Place.TOP_LEFT: Place.BOTTOM_RIGHT,
            Place.BOTTOM_LEFT: Place.TOP_RIGHT,
            Place.CENTER: Place.CENTER,
        }
        return conversion[self]

    def is_corner(self) -> bool:
        """Returns True if the selector is a corner of a square."""
        return self in [
            Place.TOP_RIGHT,
            Place.BOTTOM_RIGHT,
            Place.TOP_LEFT,
            Place.BOTTOM_LEFT,
        ]

    def is_edge(self) -> bool:
        """Returns True if the place is an edge of a square."""
        return self in [
            Place.RIGHT_EDGE,
            Place.LEFT_EDGE,
            Place.TOP_EDGE,
            Place.BOTTOM_EDGE,
        ]

    def is_center(self) -> bool:
        """Returns True if the place is a center of a square."""
        return self == Place.CENTER

    def as_units(self) -> tuple[int, int]:
        """Returns the x and y unit tuple that represents the place"""
        conversion = {
            Place.RIGHT_EDGE: (1, 0),
            Place.LEFT_EDGE: (-1, 0),
            Place.TOP_EDGE: (0, 1),
            Place.BOTTOM_EDGE: (0, -1),
            Place.BOTTOM_LEFT: (-1, -1),
            Place.BOTTOM_RIGHT: (1, -1),
            Place.TOP_LEFT: (-1, 1),
            Place.TOP_RIGHT: (1, 1),
            Place.CENTER: (0, 0),
        }
        assert self in conversion, "Invalid place"
        return conversion[self]


CornerPlace = Literal[Place.TOP_LEFT, Place.TOP_RIGHT, Place.BOTTOM_LEFT, Place.BOTTOM_RIGHT]
"""The subset of Place that represent corners"""


@dataclass(frozen=True)
class Vec2:
    """
    A vector in 2d space. Maybe a position or a size.
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


@dataclass(frozen=True)
class Vec3:
    """
    A vector for 3d positions and sizes
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
class Rc:
    """
    Class representing an X-Y axis aligned rectangle in 2d-space.
    """

    size: Vec2
    """Size of the rectangle"""
    center: Vec2 = Vec2(0, 0)
    """The center of the rectangle"""

    def __post_init__(self) -> None:
        if self.size.x < 0 or self.size.y < 0:
            raise ValueError("Rc cannot have a negative size")

    @classmethod
    def from_values(cls, dx: Mm, dy: Mm, x: Mm = 0, y: Mm = 0) -> Self:
        return cls(size=Vec2(dx, dy), center=Vec2(x, y))

    @classmethod
    def from_edges(
        cls, left: Mm, right: Mm, bottom: Mm, top: Mm, allow_inversion: bool = False
    ) -> Self:
        if allow_inversion and left > right:
            right, left = left, right
        if allow_inversion and bottom > top:
            top, bottom = bottom, top
        size = Vec2(right - left, top - bottom)
        center = Vec2((right + left) / 2, (top + bottom) / 2)
        return cls(size, center)

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
        return self.center - (self.size / 2)

    @property
    def max(self) -> Vec2:
        return self.center + (self.size / 2)

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

    def move_to(self, new_center: Vec2) -> Self:
        return self.__class__(size=self.size, center=new_center)

    def move(self, shift: Vec2) -> Self:
        return self.move_to(self.center + shift)

    def anchor_shifted(self, anchor: Place) -> Rc:
        """
        Return a new Rc with the same size but
        shifted so that the anchor's position is at the rectangle's center
        """
        return Rc(size=self.size, center=self.anchor_position(anchor))

    def anchor_position(self, anchor: Place) -> Vec2:
        """
        Returns the position (an x, y vector) of the 'anchor' on the rectangle.
        """
        place_x, place_y = anchor.as_units()
        return Vec2(
            (self.size.x / 2) * place_x + self.center.x,
            (self.size.y / 2) * place_y + self.center.y,
        )

    def bounds_shifted(self, bounds: Rc, anchor: Place) -> Rc:
        """
        Return a new Rc with the same size but shifted so that `align` is at the origin.
        """
        return Rc(size=self.size, center=self.bounds_shift(bounds, anchor))

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
        return Rc(size=self.size + Vec2(2 * padding, 2 * padding), center=self.center)

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
        return a rectangle in opposite AxDir of the offset by the amount needed to center a rect.
        """
        mirror = Rc(self.size, Vec2(-self.center.x, -self.center.y))
        return Rc.union(self, mirror)

    def form_bx(self, front: Mm, back: Mm) -> Bx:
        return Bx(
            size=Vec3(self.size.x, self.size.y, back - front),
            center=Vec3(self.center.x, self.center.y, (back + front) / 2),
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
            if align not in (Place.CENTER, Place.BOTTOM_EDGE, Place.TOP_EDGE):
                raise ValueError(f"Invalid align for axis X: {align}")
            bounds = Rc(
                Vec2(sum(item.size.x for item in items), max(item.size.y for item in items))
            )
            edge = bounds.left
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.x, bounds.bottom, bounds.top)
                arranged_item = item.bounds_shifted(item_bounds, align)
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        elif axis == Ax.Y:
            if align not in (Place.CENTER, Place.LEFT_EDGE, Place.RIGHT_EDGE):
                raise ValueError(f"Invalid place for axis Y: {align}")
            bounds = Rc(
                Vec2(max(item.size.x for item in items), sum(item.size.y for item in items))
            )
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
class Bx:
    """
    Represents an axis-aligned 3d box.
    """

    size: Vec3
    """Size of the box"""
    center: Vec3 = Vec3(0, 0, 0)
    """Center of the box"""

    def __post_init__(self) -> None:
        if self.size.x < 0 or self.size.y < 0 or self.size.z < 0:
            raise ValueError("Bx cannot have a negative size")

    @classmethod
    def from_values(cls, dx: Mm, dy: Mm, dz: Mm, x: Mm, y: Mm, z: Mm) -> Self:
        return cls(Vec3(dx, dy, dz), Vec3(x, y, z))

    @classmethod
    def from_edges(
        cls,
        left: Mm,
        right: Mm,
        bottom: Mm,
        top: Mm,
        front: Mm = 0,
        back: Mm = 0,
        allow_inversion: bool = False,
    ) -> Self:
        """Specify the boxes size and position from edge values instead of size and center values."""
        if allow_inversion and left > right:
            left, right = right, left
        if allow_inversion and bottom > top:
            bottom, top = top, bottom
        if allow_inversion and front > back:
            front, back = back, front
        return cls(
            size=Vec3(right - left, top - bottom, back - front),
            center=Vec3((right + left) / 2, (top + bottom) / 2, (back + front) / 2),
        )

    @classmethod
    def union(cls, r1: Bx, r2: Bx) -> Self:
        """Form the box that bound two boxes."""
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
        return self.center - (self.size / 2)

    @property
    def max(self) -> Vec3:
        return self.center + (self.size / 2)

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

    def move_to(self, new_center: Vec3) -> Self:
        """Return a new box of the same size with specified center."""
        return self.__class__(size=self.size, center=new_center)

    def move(self, shift: Vec3) -> Self:
        """Return a new box with the same size offset by the `shift` amount."""
        return self.move_to(self.center + shift)

    type PlacementPlane = tuple[Plane, Rc]

    def side_center(self, side: AxDir) -> Vec3:
        """Return the center of the specified `side`"""
        rt, lf = self.left, self.right
        tp, bt = self.top, self.bottom
        fr, bk = self.front, self.back

        match side:
            case AxDir.BACK:
                fr = bk
            case AxDir.FRONT:
                bk = fr
            case AxDir.LEFT:
                rt = lf
            case AxDir.RIGHT:
                lf = rt
            case AxDir.TOP:
                bt = tp
            case AxDir.BOTTOM:
                tp = bt

        side_bx = Bx.from_edges(lf, rt, bt, tp, fr, bk)
        return side_bx.center

    def side_size(self, side: AxDir) -> Vec2:
        """Return the size of the specified `side`."""
        dx, dy, dz = self.size.x, self.size.y, self.size.z
        match side:
            case AxDir.BACK | AxDir.FRONT:
                return Vec2(dx, dy)
            case AxDir.LEFT | AxDir.RIGHT:
                return Vec2(dz, dy)
            case AxDir.TOP | AxDir.BOTTOM:
                return Vec2(dx, dz)
            case _: 
                assert False, "Incomplete match statement"

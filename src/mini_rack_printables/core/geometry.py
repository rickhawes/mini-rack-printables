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

type Degree = float | int
"""A angle in degree. Used for angle specifications."""


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


class AxAlign(Enum):
    """Specify an axis and alignment. Used to align Rc in a line"""

    X = auto()
    X_BOTTOM = auto()
    X_TOP = auto()
    Y = auto()
    Y_LEFT = auto()
    Y_RIGHT = auto()

    def to_ax(self) -> Ax:
        """Converts to an axis"""
        if self in [AxAlign.X, AxAlign.X_BOTTOM, AxAlign.X_TOP]:
            return Ax.X
        else:
            return Ax.Y

    def to_anchor(self) -> Place:
        """Converts to an anchor"""
        conversion: dict[AxAlign, Place] = {
            AxAlign.X: Place.CENTER,
            AxAlign.X_BOTTOM: Place.BOTTOM_SIDE,
            AxAlign.X_TOP: Place.TOP_SIDE,
            AxAlign.Y: Place.CENTER,
            AxAlign.Y_LEFT: Place.LEFT_SIDE,
            AxAlign.Y_RIGHT: Place.RIGHT_SIDE,
        }
        assert self in conversion
        return conversion[self]


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
    FRONT = MINUS_Y
    BACK = PLUS_Y
    BOTTOM = MINUS_Z
    TOP = PLUS_Z

    def opposite(self) -> AxDir:
        conv: dict[AxDir, AxDir] = {
            AxDir.MINUS_X: AxDir.PLUS_X,
            AxDir.MINUS_Y: AxDir.PLUS_Y,
            AxDir.MINUS_Z: AxDir.PLUS_Z,
            AxDir.PLUS_X: AxDir.MINUS_X,
            AxDir.PLUS_Y: AxDir.MINUS_Y,
            AxDir.PLUS_Z: AxDir.MINUS_Z,
        }
        assert self in conv
        return conv[self]

    def z_dir(self) -> tuple[int, int, int]:
        conv: dict[AxDir, tuple[int, int, int]] = {
            AxDir.PLUS_Z: (0, 0, 1),
            AxDir.MINUS_Z: (0, 0, -1),
            AxDir.PLUS_X: (1, 0, 0),
            AxDir.MINUS_X: (-1, 0, 0),
            AxDir.PLUS_Y: (0, 1, 0),
            AxDir.MINUS_Y: (0, -1, 0),
        }
        assert self in conv
        return conv[self]

    def x_dir(self) -> tuple[int, int, int]:
        conv: dict[AxDir, tuple[int, int, int]] = {
            AxDir.PLUS_Z: (-1, 0, 0),
            AxDir.MINUS_Z: (1, 0, 0),
            AxDir.PLUS_X: (1, 0, 0),
            AxDir.MINUS_X: (-1, 0, 0),
            AxDir.PLUS_Y: (1, 0, 0),
            AxDir.MINUS_Y: (-1, 0, 0),
        }
        assert self in conv
        return conv[self]


class Place(Enum):
    """Place on a rectangle, if the rectangle was divided into 9 regions.

    Useful for specifying placing rectangles and elements with each other.
    """

    # Edge of the square
    RIGHT_SIDE = auto()
    LEFT_SIDE = auto()
    TOP_SIDE = auto()
    BOTTOM_SIDE = auto()

    # Corners of a square
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    TOP_LEFT = auto()
    BOTTOM_LEFT = auto()

    # Center of the square
    CENTER = auto()

    # Aliases for min/max axis values
    MIN_X = LEFT_SIDE
    MIN_Y = BOTTOM_SIDE
    MAX_X = RIGHT_SIDE
    MAX_Y = TOP_SIDE
    NONE = CENTER

    def opposite(self) -> Place:
        """
        Returns the opposite place reflected through the center.
        """
        conversion = {
            Place.RIGHT_SIDE: Place.LEFT_SIDE,
            Place.LEFT_SIDE: Place.RIGHT_SIDE,
            Place.TOP_SIDE: Place.BOTTOM_SIDE,
            Place.BOTTOM_SIDE: Place.TOP_SIDE,
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

    def is_side(self) -> bool:
        """Returns True if the place is a side of a square."""
        return self in [
            Place.RIGHT_SIDE,
            Place.LEFT_SIDE,
            Place.TOP_SIDE,
            Place.BOTTOM_SIDE,
        ]

    def is_center(self) -> bool:
        """Returns True if the place is a center of a square."""
        return self == Place.CENTER

    def as_units(self) -> tuple[int, int]:
        """Returns the x and y unit tuple that represents the place"""
        conversion = {
            Place.RIGHT_SIDE: (1, 0),
            Place.LEFT_SIDE: (-1, 0),
            Place.TOP_SIDE: (0, 1),
            Place.BOTTOM_SIDE: (0, -1),
            Place.BOTTOM_LEFT: (-1, -1),
            Place.BOTTOM_RIGHT: (1, -1),
            Place.TOP_LEFT: (-1, 1),
            Place.TOP_RIGHT: (1, 1),
            Place.CENTER: (0, 0),
        }
        assert self in conversion, "Invalid place"
        return conversion[self]


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
    def from_corners(cls, c1: Vec2, c2: Vec2) -> Self:
        dx, dy = abs(c1.x - c2.x), abs(c1.y - c2.y)
        return cls(size=Vec2(dx, dy), center=Vec2(dx / 2, dy))

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

    # def anchor_shifted(self, anchor: Place) -> Rc:
    #     """
    #     Return a new Rc with the same size but
    #     shifted so that the anchor's position is at the rectangle's center
    #     """
    #     return Rc(size=self.size, center=self.anchor_position(anchor))

    def place_position(self, place: Place) -> Vec2:
        """
        Returns the position (an x, y vector) of the 'place' on the rectangle.
        """
        unit_x, unit_y = place.as_units()
        return Vec2(self.size.x * unit_x, self.size.y * unit_y) / 2 + self.center

    def place_center(self, other: Rc, anchor: Place) -> Vec2:
        """
        The center of a `other` Rc that aligns `anchor` position of this Rc and the `other` Rc.
        """
        return other.place_position(anchor) - self.place_position(anchor)

    def place(self, other: Rc, anchor: Place) -> Rc:
        """
        Return a new `other` Rc moved so that `anchor` of this Rc and the `other` are aligned.
        """
        return Rc(size=self.size, center=self.place_center(other, anchor))

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

    # def centered_bounding(self) -> Rc:
    #     """
    #     return a rectangle in opposite AxDir of the offset by the amount needed to center a rect.
    #     """
    #     mirror = Rc(self.size, Vec2(-self.center.x, -self.center.y))
    #     return Rc.union(self, mirror)

    def form_bx(self, front: Mm, back: Mm) -> Bx:
        return Bx(
            size=Vec3(self.size.x, self.size.y, back - front),
            center=Vec3(self.center.x, self.center.y, (back + front) / 2),
        )

    @staticmethod
    def arrange(align: AxAlign, *items: Rc) -> list[Rc]:
        """
        Arrange a collection of Rcs along an axis and alignment.

        Args:
            align (AxAlign): The axis and align to arrange Rcs
            *items (Rc): The Rc list to arrange.

        Returns:
            list[Rc]: The arranged Rcs.
        """
        output: list[Rc] = []
        if len(items) == 0:
            return []
        if align.to_ax() == Ax.X:
            bounds = Rc(
                Vec2(sum(item.size.x for item in items), max(item.size.y for item in items))
            )
            edge = bounds.left
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.x, bounds.bottom, bounds.top)
                arranged_item = item.place(other=item_bounds, anchor=align.to_anchor())
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        elif align.to_ax() == Ax.Y:
            bounds = Rc(
                Vec2(max(item.size.x for item in items), sum(item.size.y for item in items))
            )
            edge = bounds.bottom
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.y)
                arranged_item = item.place(item_bounds, align.to_anchor())
                output.append(arranged_item)
                edge = item_bounds.top
            return output
        else:
            raise ValueError("Invalid value for align")


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
    def from_corners(cls, c1: Vec3, c2: Vec3) -> Self:
        dx, dy, dz = abs(c1.x - c2.x), abs(c1.y - c2.y), abs(c1.z - c2.z)
        return cls(Vec3(dx, dy, dz), Vec3(dx / 2, dy / 2, dz / 2))

    @classmethod
    def from_edges(
        cls,
        left: Mm,
        right: Mm,
        front: Mm,
        back: Mm,
        bottom: Mm = 0,
        top: Mm = 0,
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
            size=Vec3(right - left, back - front, top - bottom),
            center=Vec3((right + left) / 2, (back + front) / 2, (top + bottom) / 2),
        )

    @classmethod
    def union(cls, r1: Bx, r2: Bx) -> Self:
        """Form the box that bound two boxes."""
        return cls.from_edges(
            right=max(r1.right, r2.right),
            left=min(r1.left, r2.left),
            front=min(r1.front, r2.front),
            back=max(r1.back, r2.back),
            top=max(r1.top, r2.top),
            bottom=min(r1.bottom, r2.bottom),
        )

    @property
    def min(self) -> Vec3:
        return self.center - (self.size / 2)

    @property
    def max(self) -> Vec3:
        return self.center + (self.size / 2)

    @property
    def left(self) -> Mm:
        return self.min.x

    @property
    def right(self) -> Mm:
        return self.max.x

    @property
    def front(self) -> Mm:
        return self.min.y

    @property
    def back(self) -> Mm:
        return self.max.y

    @property
    def top(self) -> Mm:
        return self.max.z

    @property
    def bottom(self) -> Mm:
        return self.min.z

    def move_to(self, new_center: Vec3) -> Self:
        """Return a new box of the same size with specified center."""
        return self.__class__(size=self.size, center=new_center)

    def move(self, shift: Vec3) -> Self:
        """Return a new box with the same size offset by the `shift` amount."""
        return self.move_to(self.center + shift)

    # Information about a side of a box

    def side_center(self, side: AxDir) -> Vec3:
        """Return the center of the specified `side`"""
        lf, rt = self.left, self.right
        fr, bk = self.front, self.back
        bt, tp = self.bottom, self.top

        match side:
            case AxDir.LEFT:
                rt = lf
            case AxDir.RIGHT:
                lf = rt
            case AxDir.BACK:
                fr = bk
            case AxDir.FRONT:
                bk = fr
            case AxDir.TOP:
                bt = tp
            case AxDir.BOTTOM:
                tp = bt

        side_bx = Bx.from_edges(left=lf, right=rt, front=fr, back=bk, bottom=bt, top=tp)
        return side_bx.center

    def side_size(self, side: AxDir) -> Vec2:
        """Return the size of the specified `side`."""
        dx, dy, dz = self.size.x, self.size.y, self.size.z
        match side:
            case AxDir.MINUS_X | AxDir.PLUS_X:
                return Vec2(dy, dz)
            case AxDir.MINUS_Y | AxDir.PLUS_Y:
                return Vec2(dx, dz)
            case AxDir.MINUS_Z | AxDir.PLUS_Z:
                return Vec2(dx, dy)
            case _:
                assert False, "Incomplete match statement"

    def side_depth(self, side: AxDir) -> Mm:
        """Return the depth of the specified `side`."""
        match side:
            case AxDir.MINUS_X | AxDir.PLUS_X:
                return self.size.x
            case AxDir.MINUS_Y | AxDir.PLUS_Y:
                return self.size.y
            case AxDir.MINUS_Z | AxDir.PLUS_Z:
                return self.size.z
            case _:
                assert False, "Incomplete match statement"

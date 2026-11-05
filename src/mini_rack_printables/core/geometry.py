"""Classes to specify box and rectangle dimensions and positions.

Contains 1D, 2D and 3D sections.

See Also:
    `Figure`, `Block` - Main user of geometry

"""

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Self

import build123d as bd

# ------------------------------------------------------------------------------
# 1D Classes and Enums
# ------------------------------------------------------------------------------

type Mm = float | int
"""A millimeter measurement value. Used for all length measurements in the library."""

type Degree = float | int
"""A angle in degree. Used for angle specifications."""


class AxDir(IntEnum):
    """A positive, neutral, or negative direction.
    Used for in forming 2d and 3d directions."""

    PLUS = 1
    MINUS = -1
    CENTER = 0


# ------------------------------------------------------------------------------
# 2D Classes and Enums
# ------------------------------------------------------------------------------


class Ax2(Enum):
    """The X or Y axis in 2d space."""

    X = auto()
    """ X axis """
    Y = auto()
    """ Y axis """


class Dir2(Enum):
    """
    A direction in 2d space.

    A Dir2 is not a vector, but used to specify the sections, edges, and corners
    of a rectangle.For a square centered at 0, 0, the x, y values of the enum will
    specify a corner, side or center sections.

    See Also:
        AxDir2 -- Subset directions of Dir2
        Rc.place() -- Use of a Dir2 to place a rectangle
    """

    x: AxDir
    y: AxDir

    # Main enumeration in X, Y ascending order
    CORNER_LF_BT = (-1, -1)
    Y_MINUS = (0, -1)
    CORNER_RT_BT = (1, -1)
    X_MINUS = (-1, 0)
    CENTER = (0, 0)
    X_PLUS = (1, 0)
    CORNER_LF_TP = (-1, 1)
    Y_PLUS = (0, 1)
    CORNER_RT_TP = (1, 1)

    # Alias names for sides
    SIDE_BOTTOM = Y_MINUS
    SIDE_LEFT = X_MINUS
    SIDE_RIGHT = X_PLUS
    SIDE_TOP = Y_PLUS

    def __init__(self, x: AxDir, y: AxDir) -> None:
        """Specify a direction in 2d space.

        Args:
            x (AxDir): X axis direction
            y (AxDir): Y axis direction
        """
        self.x = x
        self.y = y

    @property
    def is_side(self) -> bool:
        """Is the this a side"""
        return (self.x, self.y).count(AxDir.CENTER) == 1

    def __neg__(self) -> Dir2:
        """Opposite direction"""
        return Dir2(-self.x, -self.y)

    def to_opposite(self) -> Dir2:
        """Opposite direction"""
        return -self

    def to_ax_dir2(self) -> AxDir2 | None:
        """Covert to an AxDir2, if possible. None otherwise."""
        return AxDir2(self.x, self.y) if self.is_side else None


class AxDir2(Enum):
    """The set of directions which are axis aligned.

    See Also:
        Dir2 - A fuller set of directions.
    """

    x: AxDir
    y: AxDir

    # Axis aligned directions
    X_MINUS = (-1, 0)
    X_PLUS = (1, 0)
    Y_MINUS = (0, -1)
    Y_PLUS = (0, 1)

    # Colloquial Aliases
    LEFT = X_MINUS
    RIGHT = X_PLUS
    BOTTOM = Y_MINUS
    TOP = Y_PLUS

    def __init__(self, x: AxDir, y: AxDir) -> None:
        if (x, y).count(AxDir.CENTER) != 1:
            raise ValueError("x == CENTER and y == CENTER must be exclusive")
        self.x = x
        self.y = y

    @property
    def is_x(self) -> bool:
        """True iff the AxDir is in the x direction."""
        return self.x != AxDir.CENTER

    @property
    def is_y(self) -> bool:
        """True iff the AxDir is in the y direction."""
        return self.y != AxDir.CENTER

    @property
    def is_positive(self) -> bool:
        """True iff the AxDir is in a positive direction"""
        return self in [AxDir2.X_PLUS, AxDir2.Y_PLUS]

    def __neg__(self) -> AxDir2:
        return AxDir2(-self.x, -self.y)

    def to_opposite(self) -> AxDir2:
        """The opposite direction along the same axis direction."""
        return -self

    def to_ax2(self) -> Ax2:
        """Covert to an Ax2."""
        return Ax2.X if self.is_x else Ax2.Y

    def to_other_ax2(self) -> Ax2:
        """Covert to the other axis. For an x-axis, an Ax.Y will be returned."""
        return Ax2.Y if self.is_x else Ax2.X

    def to_dir2(self) -> Dir2:
        """Covert to a Dir2."""
        return Dir2(self.x, self.y)

    def to_vec2(self) -> Vec2:
        """Convert to a Vec2"""
        return Vec2(self.x, self.y)


@dataclass(frozen=True)
class Vec2:
    """
    A vector in 2d space. Maybe a position or a size.

    +, -, *, /, operators are provided to perform mathematical operations on Vec2

    Example:
        v = Vec2(1, 2) + Vec2(3, 4)
        print(v)
        # Vec2(x=4, y=6)
        print(2*v)
        # Vec2(x=8, y=12)
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

    def to_vec3(self, z: Mm = 0) -> Vec3:
        """Convert to a Vec3"""
        return Vec3(self.x, self.y, z)

    def to_vector(self) -> bd.Vector:
        """Convert to a build123d Vector."""
        return bd.Vector(self.x, self.y)

    def to_tuple(self) -> tuple[Mm, Mm]:
        """Convert to a tuple with the components"""
        return self.x, self.y

    @classmethod
    def from_vector(cls, vec: bd.Vector) -> Vec2:
        """Covert from a build123d vector."""
        return Vec2(vec.X, vec.Y)


@dataclass(frozen=True, init=False)
class Rc:
    """
    Class representing an X-Y axis aligned rectangle in 2d-space.
    """

    # pyrefly: ignore[uninitialized-instance-variable]
    size: Vec2
    """Size of the rectangle"""
    center: Vec2 = Vec2(0, 0)
    """The center of the rectangle"""

    def __init__(self, *args: Mm | Vec2 | tuple[Mm, Mm]) -> None:
        """Create from size and center. Center defaults to zero."""
        match len(args):
            case 1 if isinstance(args[0], Vec2):
                object.__setattr__(self, "size", args[0])
            case 1 if isinstance(args[0], tuple[int | float, int | float]):
                object.__setattr__(self, "size", Vec2(args[0][0], args[0][1]))
            case 2 if isinstance(args[0], Vec2):
                object.__setattr__(self, "size", args[0])
                object.__setattr__(self, "center", args[1])
            case 2 if isinstance(args[0], tuple) and isinstance(args[1], tuple):
                object.__setattr__(self, "size", Vec2(args[0][0], args[0][1]))
                object.__setattr__(self, "center", Vec2(args[1][0], args[1][1]))
            case 2 if isinstance(args[0], int | float) and isinstance(
                args[1], int | float
            ):
                object.__setattr__(self, "size", Vec2(args[0], args[1]))
            case 4 if (
                isinstance(args[0], int | float)
                and isinstance(args[1], int | float)
                and isinstance(args[2], int | float)
                and isinstance(args[3], int | float)
            ):
                object.__setattr__(self, "size", Vec2(args[0], args[1]))
                object.__setattr__(self, "center", Vec2(args[2], args[3]))
            case _:
                raise ValueError("Improper arguments, must be 2 or 4 Mm or 1 or 2 Vec2")
        if self.size.x < 0 or self.size.y < 0:
            raise ValueError("Rc cannot have a negative size")

    @classmethod
    def from_values(cls, dx: Mm, dy: Mm, x: Mm = 0, y: Mm = 0) -> Self:
        """Make from specific values"""
        return cls(Vec2(dx, dy), Vec2(x, y))

    @classmethod
    def from_edges(
        cls, left: Mm, right: Mm, bottom: Mm, top: Mm, allow_inversion: bool = False
    ) -> Self:
        """Make from the edge values."""
        if allow_inversion and left > right:
            right, left = left, right
        if allow_inversion and bottom > top:
            top, bottom = bottom, top
        size = Vec2(right - left, top - bottom)
        center = Vec2((right + left) / 2, (top + bottom) / 2)
        return cls(size, center)

    @classmethod
    def from_corners(cls, c1: Vec2, c2: Vec2) -> Self:
        """Make from corner points."""
        dx, dy = abs(c1.x - c2.x), abs(c1.y - c2.y)
        return cls(Vec2(dx, dy), Vec2(dx / 2, dy))

    @classmethod
    def union(cls, *rcs: Rc) -> Self:
        """Union multiple rectangles."""
        return cls.from_edges(
            right=max(r.right for r in rcs),
            left=min(r.left for r in rcs),
            top=max(r.top for r in rcs),
            bottom=min(r.bottom for r in rcs),
        )

    @property
    def min(self) -> Vec2:
        """The lower-left corner."""
        return self.center - (self.size / 2)

    @property
    def max(self) -> Vec2:
        """The upper-right corner."""
        return self.center + (self.size / 2)

    @property
    def top(self) -> Mm:
        """The top edge (Y)."""
        return self.max.y

    @property
    def bottom(self) -> Mm:
        """The bottom edge (Y)"""
        return self.min.y

    @property
    def left(self) -> Mm:
        """The left edge (X)."""
        return self.min.x

    @property
    def right(self) -> Mm:
        """The right edge (X)."""
        return self.max.x

    def is_within(self, outside: Rc) -> bool:
        """Is this rect within an `outside` Rc."""
        return (
            self.min.x >= outside.min.x
            and self.min.y >= outside.min.y
            and self.max.x <= outside.max.x
            and self.max.y <= outside.max.y
        )

    def move_to(self, new_center: Vec2) -> Self:
        """New Rc with a new center."""
        return self.__class__(self.size, new_center)

    def move(self, shift: Vec2) -> Self:
        """New Rc with a new center shifted relative to the old center."""
        return self.move_to(self.center + shift)

    def dir_position(self, place: Dir2) -> Vec2:
        """
        Returns the position (x,y) of the 'dir' on the rectangle.
        'dir' can specify a corner, a side, or the center of the rectangle.
        """
        return Vec2(self.size.x * place.x, self.size.y * place.y) / 2 + self.center

    def place_center(self, other: Rc, place: Dir2) -> Vec2:
        """
        The center of a `other` Rc that aligns the `place` position of
        this Rc and the `other` Rc.
        """
        return self.dir_position(place) - other.dir_position(place)

    def place(self, other: Rc, place: Dir2) -> Rc:
        """
        Return a new `other` Rc moved so that `anchor` of this Rc and
        the `other` are aligned.
        """
        return Rc(other.size, self.place_center(other, place))

    def apply_padding(self, padding: Mm) -> Rc:
        """
        Apply padding to the Rc, expanding its size by `padding` amount
        but not shifting its center.
        """
        return Rc(self.size + Vec2(2 * padding, 2 * padding), self.center)

    def to_bx(
        self,
        dz: Mm | None = None,
        z: Mm | None = None,
        bottom: Mm | None = None,
        top: Mm | None = None,
    ) -> Bx:
        """Convert to a Bx with the specified z values. 0 is the default."""
        if (dz is not None or z is not None) and (
            bottom is not None or top is not None
        ):
            raise ValueError(
                "Over specified, either (dz, z) or (front or back) must be None"
            )
        if (bottom is not None and top is None) or (bottom is None and top is not None):
            raise ValueError(
                "Both top and bottom must be specified if one is specified"
            )
        if bottom is not None and top is not None:
            dz = top - bottom
            z = (top + bottom) / 2
        if z is None:
            z = 0
        if dz is None:
            dz = 0
        assert dz is not None and z is not None
        return Bx(
            Vec3(self.size.x, self.size.y, dz),
            Vec3(self.center.x, self.center.y, z),
        )

    @staticmethod
    def arrange(axis: Ax2, align: AxDir, *items: Rc) -> list[Rc]:
        """
        Arrange a collection of Rcs along an axis and alignment.

        Args:
            axis: (AxDir2) - the direction to layout
            align: (AxDir) - the alignment direction
            *items (Rc): The Rc list to arrange.

        Returns:
            list[Rc]: The arranged Rcs.
        """

        if len(items) == 0:
            return []
        output: list[Rc] = []
        if axis == Ax2.X:
            bounds = Rc(
                Vec2(
                    sum(item.size.x for item in items),
                    max(item.size.y for item in items),
                )
            )
            edge = bounds.left
            for item in items:
                edge_right = edge + item.size.x
                item_bounds = Rc.from_edges(edge, edge_right, bounds.bottom, bounds.top)
                arranged_item = item_bounds.place(item, Dir2(AxDir.CENTER, align))
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        if axis == Ax2.Y:
            bounds = Rc(
                Vec2(
                    max(item.size.x for item in items),
                    sum(item.size.y for item in items),
                )
            )
            edge = bounds.bottom
            for item in items:
                edge_top = edge + item.size.y
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge_top)
                arranged_item = item_bounds.place(item, Dir2(align, AxDir.CENTER))
                output.append(arranged_item)
                edge = item_bounds.top
            return output
        raise NotImplementedError()


# ------------------------------------------------------------------------------
# 3D Classes and Enums
# ------------------------------------------------------------------------------


class Ax3(Enum):
    """Axis X, Y or Z"""

    X = auto()
    """ X axis """
    Y = auto()
    """ Y axis """
    Z = auto()
    """ Z axis """


class Dir3(Enum):
    """A direction in 3d space.

    A Dir3 is not a vector, but used to specify the sections, edges, and corners
    of a cube. For a 2x2x2 cube centered at 0, 0, the x, y, z values of the
    enum will specify the corner edge or a center sections.

    See Also:
        AxDir3 - Subset directions of Dir3
        Rc.place() - Use of a Dir3 to place a rectangle
    """

    x: AxDir
    y: AxDir
    z: AxDir

    # Main enumeration in Z, Y, X ascending order (TP/BT,
    CORNER_LF_FT_BT = (-1, -1, -1)
    EDGE_FT_BT = (0, -1, -1)
    CORNER_RT_FT_BT = (1, -1, -1)

    EDGE_LF_BT = (-1, 0, -1)
    Z_MINUS = (0, 0, -1)
    EDGE_RT_BT = (1, 0, -1)

    CORNER_LF_BK_BT = (-1, 1, -1)
    EDGE_BK_BT = (0, 1, -1)
    CORNER_RT_BK_BT = (1, 1, -1)

    EDGE_LF_FT = (-1, -1, 0)
    Y_MINUS = (0, -1, 0)
    EDGE_RT_FT = (1, -1, 0)

    X_MINUS = (-1, 0, 0)
    CENTER = (0, 0, 0)
    X_PLUS = (1, 0, 0)

    EDGE_LF_BK = (-1, 1, 0)
    Y_PLUS = (0, 1, 0)
    EDGE_RT_BK = (1, 1, 0)

    CORNER_LF_FT_TP = (-1, -1, 1)
    EDGE_FT_TP = (0, -1, 1)
    CORNER_RT_FT_TP = (1, -1, 1)

    EDGE_LF_TP = (-1, 0, 1)
    Z_PLUS = (0, 0, 1)
    EDGE_RT_TP = (1, 0, 1)

    CORNER_LF_BK_TP = (-1, 1, 1)
    EDGE_BK_TP = (0, 1, 1)
    CORNER_RT_BK_TP = (1, 1, 1)

    # Alias names for side
    SIDE_LEFT = X_MINUS
    SIDE_RIGHT = X_PLUS
    SIDE_FRONT = Y_MINUS
    SIDE_BACK = Y_PLUS
    SIDE_BOTTOM = Z_MINUS
    SIDE_TOP = Z_PLUS

    def __init__(self, x: AxDir, y: AxDir, z: AxDir) -> None:
        """Specify a dir in 2d space.

        Args:
            x (AxDir): X axis direction
            y (AxDir): Y axis direction
            z (AxDir): Z axis direction
        """
        self.x = x
        self.y = y
        self.z = z

    @property
    def is_side(self) -> bool:
        """Is the this a side direction"""
        return (self.x, self.y, self.z).count(AxDir.CENTER) == 2

    def __neg__(self) -> Dir3:
        """Negative direction"""
        return Dir3(-self.x, -self.y, -self.z)

    def to_opposite(self) -> Dir3:
        """Opposite direction"""
        return -self

    def to_ax_dir3(self) -> AxDir3 | None:
        """Covert to an AxDir3, if possible. None otherwise."""
        return AxDir3(self.x, self.y, self.z) if self.is_side else None


class AxDir3(Enum):
    """Enum for the 6 axis aligned AxDirs from the 0,0,0 origin.

    Useful to specify the AxDir of a stack, or the side of the box,
    or the z-dir of a `Plane`. The default X-Y Plane has a z-axis
    direction of AxDir.PLUS_Z.
    """

    X_MINUS = (-1, 0, 0)
    X_PLUS = (1, 0, 0)
    Y_MINUS = (0, -1, 0)
    Y_PLUS = (0, 1, 0)
    Z_MINUS = (0, 0, -1)
    Z_PLUS = (0, 0, 1)

    # Colloquial names for AxDir
    LEFT = X_MINUS
    RIGHT = X_PLUS
    FRONT = Y_MINUS
    BACK = Y_PLUS
    BOTTOM = Z_MINUS
    TOP = Z_PLUS

    def __init__(self, x: AxDir, y: AxDir, z: AxDir) -> None:
        """Create a 3d AxDir"""
        if (x, y, z).count(AxDir.CENTER) != 2:
            raise ValueError(f"Only one axis direction {x, y, z}")
        self.x = x
        self.y = y
        self.z = z

    @property
    def has_x(self) -> bool:
        """Does this direction have a x component."""
        return self.x != AxDir.CENTER

    @property
    def has_y(self) -> bool:
        """Does this direction have a y component."""
        return self.y != AxDir.CENTER

    @property
    def has_z(self) -> bool:
        """Does this direction have a z component."""
        return self.z != AxDir.CENTER

    @property
    def is_positive(self) -> bool:
        """Is the direction positive"""
        return self in [
            AxDir3.X_PLUS,
            AxDir3.Y_PLUS,
            AxDir3.Z_PLUS,
        ]

    def __neg__(self) -> AxDir3:
        return AxDir3(-self.x, -self.y, -self.z)

    def to_opposite(self) -> AxDir3:
        """Return the opposite direction"""
        return -self

    def to_dir3(self) -> Dir3:
        """Convert to a Dir3"""
        return Dir3(self.x, self.y, self.z)

    def to_plane_z_dir(self) -> tuple[int, int, int]:
        """Covert to the z_dir of a Build123d Plane"""
        return self.x, self.y, self.z

    def to_plane_x_dir(self) -> tuple[int, int, int]:
        """Covert to the x_dir of a Build123d Plane"""
        conv: dict[AxDir3, tuple[int, int, int]] = {
            AxDir3.Z_PLUS: (1, 0, 0),
            AxDir3.Z_MINUS: (-1, 0, 0),
            AxDir3.X_PLUS: (0, 1, 0),
            AxDir3.X_MINUS: (0, -1, 0),
            AxDir3.Y_PLUS: (-1, 0, 0),
            AxDir3.Y_MINUS: (1, 0, 0),
        }
        assert self in conv
        return conv[self]

    def to_vec3(self) -> Vec3:
        """Convert to a Vec3."""
        return Vec3(self.x, self.y, self.z)


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
        """Convert to a Vec2 using only the xy components"""
        return Vec2(self.x, self.y)

    def to_vector(self) -> bd.Vector:
        """Convert the build123d type."""
        return bd.Vector(self.x, self.y, self.z)

    def to_tuple(self) -> tuple[Mm, Mm, Mm]:
        """A tuple with all components."""
        return self.x, self.y, self.z

    @classmethod
    def from_vector(cls, vec: bd.Vector) -> Vec3:
        """Make from the build123d vector"""
        return Vec3(vec.X, vec.Y, vec.Z)


@dataclass(frozen=True, init=False)
class Bx:
    """
    Represents an axis-aligned 3d box.
    """

    # pyrefly: ignore[uninitialized-instance-variable]
    size: Vec3
    """Size of the box"""
    center: Vec3 = Vec3(0, 0, 0)
    """Center of the box"""

    def __init__(self, *args: Mm | Vec3 | tuple[Mm, Mm, Mm]) -> None:
        """Create with size and center. center defaults to zero.

        Args:
            args (Mm, Vec3, tuple): the size and then center of the box

        """
        match len(args):
            case 1 if isinstance(args[0], Vec3):
                object.__setattr__(self, "size", args[0])
            case 1 if isinstance(args[0], tuple):
                object.__setattr__(
                    self, "size", Vec3(args[0][0], args[0][1], args[0][2])
                )
            case 2 if isinstance(args[0], Vec3):
                object.__setattr__(self, "size", args[0])
                object.__setattr__(self, "center", args[1])
            case 2 if isinstance(args[0], tuple) and isinstance(args[1], tuple):
                object.__setattr__(
                    self, "size", Vec3(args[0][0], args[0][1], args[0][2])
                )
                object.__setattr__(
                    self, "center", Vec3(args[1][0], args[1][1], args[1][2])
                )
            case 3 if (
                isinstance(args[0], int | float)
                and isinstance(args[1], int | float)
                and isinstance(args[2], int | float)
            ):
                object.__setattr__(self, "size", Vec3(args[0], args[1], args[2]))
            case 6 if (
                isinstance(args[0], int | float)
                and isinstance(args[1], int | float)
                and isinstance(args[2], int | float)
                and isinstance(args[3], int | float)
                and isinstance(args[4], int | float)
                and isinstance(args[5], int | float)
            ):
                object.__setattr__(self, "size", Vec3(args[0], args[1], args[2]))
                object.__setattr__(self, "center", Vec3(args[3], args[4], args[5]))
            case _:
                raise ValueError("Improper arguments, must be 3 or 6 Mm or 1 or 2 Vec3")
        if self.size.x < 0 or self.size.y < 0:
            raise ValueError("Bx cannot have a negative size")

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    @classmethod
    def from_values(cls, dx: Mm, dy: Mm, dz: Mm, x: Mm, y: Mm, z: Mm) -> Self:
        """Make from values."""
        return cls(Vec3(dx, dy, dz), Vec3(x, y, z))

    @classmethod
    def from_corners(cls, c1: Vec3, c2: Vec3) -> Self:
        """Make from the specified corners"""
        dx, dy, dz = abs(c1.x - c2.x), abs(c1.y - c2.y), abs(c1.z - c2.z)
        return cls(Vec3(dx, dy, dz), Vec3(dx / 2, dy / 2, dz / 2))

    # pylint: disable=too-many-arguments, too-many-positional-arguments
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
        """Specify the boxes size and position from edge values instead of size and
        center values."""
        if allow_inversion and left > right:
            left, right = right, left
        if allow_inversion and bottom > top:
            bottom, top = top, bottom
        if allow_inversion and front > back:
            front, back = back, front
        return cls(
            Vec3(right - left, back - front, top - bottom),
            Vec3((right + left) / 2, (back + front) / 2, (top + bottom) / 2),
        )

    @classmethod
    def from_side_rc(
        cls,
        side: AxDir3,
        rc: Rc,
        depth: Mm = 0,
        offset: Mm = 0,
    ) -> Bx:
        """Create a from a side, rc, and depth."""
        center = offset
        match side:
            case AxDir3.X_MINUS | AxDir3.X_PLUS:
                return Bx(depth, rc.size.x, rc.size.y, center, rc.center.x, rc.center.y)
            case AxDir3.Y_MINUS | AxDir3.Y_PLUS:
                return Bx(rc.size.x, depth, rc.size.y, rc.center.x, center, rc.center.y)
            case AxDir3.Z_MINUS | AxDir3.Z_PLUS:
                return Bx(rc.size.x, rc.size.y, depth, rc.center.x, rc.center.y, center)
            case _:
                raise ValueError("unexpected side")

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
        """The lower corner."""
        return self.center - (self.size / 2)

    @property
    def max(self) -> Vec3:
        """The upper corner."""
        return self.center + (self.size / 2)

    @property
    def left(self) -> Mm:
        """The left x edge."""
        return self.min.x

    @property
    def right(self) -> Mm:
        """The right x edge."""
        return self.max.x

    @property
    def front(self) -> Mm:
        """The front y-edge."""
        return self.min.y

    @property
    def back(self) -> Mm:
        """The back y-edge."""
        return self.max.y

    @property
    def top(self) -> Mm:
        """The top z edge."""
        return self.max.z

    @property
    def bottom(self) -> Mm:
        """The bottom z edge."""
        return self.min.z

    def move_to(self, new_center: Vec3) -> Self:
        """Return a new box of the same size with specified center."""
        return self.__class__(self.size, new_center)

    def move(self, shift: Vec3) -> Self:
        """Return a new box with the same size offset by the `shift` amount."""
        return self.move_to(self.center + shift)

    # Information about a side of a box

    def side_bx(self, side: AxDir3) -> Bx:
        """Return the center of the specified `side`"""
        lf, rt = self.left, self.right
        fr, bk = self.front, self.back
        bt, tp = self.bottom, self.top

        match side:
            case AxDir3.LEFT:
                rt = lf
            case AxDir3.RIGHT:
                lf = rt
            case AxDir3.BACK:
                fr = bk
            case AxDir3.FRONT:
                bk = fr
            case AxDir3.TOP:
                bt = tp
            case AxDir3.BOTTOM:
                tp = bt

        return Bx.from_edges(left=lf, right=rt, front=fr, back=bk, bottom=bt, top=tp)

    def side_size(self, side: AxDir3) -> Vec2:
        """Return the size of the specified `side`."""
        dx, dy, dz = self.size.x, self.size.y, self.size.z
        match side:
            case AxDir3.X_MINUS | AxDir3.X_PLUS:
                return Vec2(dy, dz)
            case AxDir3.Y_MINUS | AxDir3.Y_PLUS:
                return Vec2(dx, dz)
            case AxDir3.Z_MINUS | AxDir3.Z_PLUS:
                return Vec2(dx, dy)
            case _:
                assert False, "Incomplete match statement"

    def side_depth(self, side: AxDir3) -> Mm:
        """Return the depth of the specified `side`."""
        match side:
            case AxDir3.X_MINUS | AxDir3.X_PLUS:
                return self.size.x
            case AxDir3.Y_MINUS | AxDir3.Y_PLUS:
                return self.size.y
            case AxDir3.Z_MINUS | AxDir3.Z_PLUS:
                return self.size.z
            case _:
                assert False, "Incomplete match statement"

    def side_rc(self, side: AxDir3) -> Rc:
        """Return the Rc of the specified side."""
        size = self.side_size(side)
        center = self.side_bx(side).center
        match side:
            case AxDir3.X_MINUS | AxDir3.X_PLUS:
                return Rc(size, Vec2(center.y, center.z))
            case AxDir3.Y_MINUS | AxDir3.Y_PLUS:
                return Rc(size, Vec2(center.x, center.z))
            case AxDir3.Z_MINUS | AxDir3.Z_PLUS:
                return Rc(size, Vec2(center.x, center.y))
            case _:
                assert False, "Incomplete match statement"

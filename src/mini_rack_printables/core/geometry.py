"""Classes to specify box and rectangle dimensions and positions.

Contains 1D, 2D and 3D sections.

See Also:
    Placement - Enums to position and align boxes and rectangles
    Element2D, Element3D - Main user of geometry

"""

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Self

from build123d import Vector

# ------------------------------------------------------------------------------
# 1D Classes and Enums
# ------------------------------------------------------------------------------

type Mm = float | int
"""A millimeter measurement value. Used for all length measurements in the library."""

type Degree = float | int
"""A angle in degree. Used for angle specifications."""


class AxDir(IntEnum):
    """A positive, neutral, or negative direction. Used for in forming 2d and 3d directions."""

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

    def to_other(self):
        """Convert to the other Ax2 axis."""
        return Ax2.X if self == Ax2.Y else Ax2.Y


class Dir2(Enum):
    """
    A direction in 2d space.

    A Dir2 is not a vector, but used to specify the sections, edges, and corners of a rectangle.
    For a square centered at 0, 0, the x, y values of the enum will specify a corner, side or center sections.

    See Also:
        AxDir2, Corner2 -- Subset directions of Dir2
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

    @classmethod
    def corners(cls):
        """A set of Dir2's which correspond to the corners of a rectangle."""
        return frozenset({cls.CORNER_LF_BT, cls.CORNER_LF_TP, cls.CORNER_RT_BT, cls.CORNER_RT_TP})

    @classmethod
    def sides(cls):
        """A set of Dir2's which correspond to the sides of a rectangle."""
        return frozenset({cls.SIDE_BOTTOM, cls.SIDE_LEFT, cls.SIDE_RIGHT, cls.SIDE_TOP})

    @property
    def is_corner(self) -> bool:
        """Does the direction represent a corner?"""
        return self in Dir2.corners()

    @property
    def is_side(self) -> bool:
        """Does the direction represent a side?"""
        return self in Dir2.sides()

    @property
    def is_center(self) -> bool:
        """Does the direction represent a center?"""
        return self == Dir2.CENTER

    def __neg__(self) -> Dir2:
        """Opposite direction"""
        return Dir2(-self.x, -self.y)

    def to_opposite(self) -> Dir2:
        """Opposite direction"""
        return -self

    def to_ax_dir2(self) -> AxDir2 | None:
        """Covert to an AxDir2, if possible. None otherwise."""
        return AxDir2(self.x, self.y) if self.is_side else None

    def to_corners(self) -> list[Corner2]:
        """List the Corner2's associated with this Dir2.

        If this is a center direction, then an empty list is returned.
        If this is a side direction, then two corners are returned.
        """
        if self.is_center:
            return []
        elif (ax := self.to_ax_dir2()) is not None:
            if ax.is_x:
                return [Corner2(self.x, AxDir.MINUS), Corner2(self.x, AxDir.PLUS)]
            else:
                return [Corner2(AxDir.MINUS, self.y), Corner2(AxDir.PLUS, self.y)]
        else:
            return [Corner2(self.x, self.y)]


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
        if x == AxDir.CENTER and y == AxDir.CENTER or x != AxDir.CENTER and y != AxDir.CENTER:
            raise ValueError("x == CENTER and y == CENTER must be exclusive")
        self.x = x
        self.y = y

    @property
    def is_x(self):
        """True iff the AxDir is in the x direction."""
        return self.x != AxDir.CENTER

    @property
    def is_y(self):
        """True iff the AxDir is in the y direction."""
        return self.y != AxDir.CENTER

    def __neg__(self) -> AxDir2:
        return AxDir2(-self.x, -self.y)

    def to_opposite(self) -> AxDir2:
        """The opposite direction along the same axis direction."""
        return -self

    def to_ax2(self) -> Ax2:
        """Covert to an Ax2."""
        return Ax2.X if self.is_x else Ax2.Y

    def to_other_ax2(self) -> Ax2:
        """Covert to the other axis. For a x-axis."""
        return Ax2.Y if self.is_x else Ax2.X

    def to_dir2(self) -> Dir2:
        """Covert to a Dir2."""
        return Dir2(self.x, self.y)


class Corner2(Enum):
    """Enum which corresponds with the four corners of a rectangle"""
    x: AxDir
    y: AxDir

    LT_BT = (-1, -1)
    RT_BT = (1, -1)
    LT_TP = (-1, 1)
    RT_TP = (1, 1)

    def __init__(self, x: AxDir, y: AxDir) -> None:
        """
        A corner of a rectangle.

        Args:
            x (AxDir): X direction
            y (AxDir): Y direction
        """
        if x == AxDir.CENTER or y == AxDir.CENTER:
            raise ValueError("Only corners values are valid")
        self.x = x
        self.y = y

    def __neg__(self) -> Corner2:
        return Corner2(-self.x, -self.y)

    def opposite(self) -> Corner2:
        """Return the opposite corner of the corner."""
        return -self

    def to_dir2(self) -> Dir2:
        """Covert to a Dir2 direction."""
        return Dir2(self.x, self.y)


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

    def to_3d(self, z: Mm = 0) -> Vec3:
        return Vec3(self.x, self.y, z)

    def to_vector(self) -> Vector:
        return Vector(self.x, self.y)

    def to_tuple(self) -> tuple[Mm, Mm]:
        return self.x, self.y


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

    def dir_position(self, place: Dir2) -> Vec2:
        """
        Returns the position (x,y) of the 'dir' on the rectangle. 'dir' can specify a corner, a side,
        or the center of the rectangle.
        """
        return Vec2(self.size.x * place.x, self.size.y * place.y) / 2 + self.center

    def place_center(self, other: Rc, place: Dir2) -> Vec2:
        """
        The center of a `other` Rc that aligns the `place` position of this Rc and the `other` Rc.
        """
        return self.dir_position(place) - other.dir_position(place)

    def place(self, other: Rc, place: Dir2) -> Rc:
        """
        Return a new `other` Rc moved so that `anchor` of this Rc and the `other` are aligned.
        """
        return Rc(size=other.size, center=self.place_center(other, place))

    def apply_padding(self, padding: Mm) -> Rc:
        """
        Apply padding to the Rc, expanding its size by `padding` amount but not shifting its center.
        """
        return Rc(size=self.size + Vec2(2 * padding, 2 * padding), center=self.center)

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
                Vec2(sum(item.size.x for item in items), max(item.size.y for item in items))
            )
            edge = bounds.left
            for item in items:
                item_bounds = Rc.from_edges(edge, edge + item.size.x, bounds.bottom, bounds.top)
                arranged_item = item_bounds.place(other=item, place=Dir2(AxDir.CENTER, align))
                output.append(arranged_item)
                edge = item_bounds.right
            return output
        elif axis == Ax2.Y:
            bounds = Rc(
                Vec2(max(item.size.x for item in items), sum(item.size.y for item in items))
            )
            edge = bounds.bottom
            for item in items:
                item_bounds = Rc.from_edges(bounds.left, bounds.right, edge, edge + item.size.y)
                arranged_item = item_bounds.place(other=item, place=Dir2(align, AxDir.CENTER))
                output.append(arranged_item)
                edge = item_bounds.top
            return output
        else:
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
    """
    A direction in 3d space.

    A Dir3 is not a vector, but used to specify the sections, edges, and corners of a cube.
    For a 2x2x2 cube centered at 0, 0, the x, y, z values of the enum will specify the corner edge or an center sections.

    See Also:
        AxDir3, Corner2 -- Subset directions of Dir3
        Rc.place() -- Use of a Dir3 to place a rectangle
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

    @classmethod
    def corners(cls):
        """A set of Dir3's which represent corners"""
        return frozenset(
            {
                cls.CORNER_LF_BK_BT,
                cls.CORNER_LF_BK_TP,
                cls.CORNER_LF_FT_BT,
                cls.CORNER_LF_FT_TP,
                cls.CORNER_RT_BK_BT,
                cls.CORNER_RT_BK_TP,
                cls.CORNER_RT_FT_BT,
                cls.CORNER_RT_FT_TP,
            }
        )

    @classmethod
    def edges(cls):
        """A set of Dir3's which represent edges"""
        return frozenset(
            {
                cls.EDGE_BK_BT,
                cls.EDGE_BK_TP,
                cls.EDGE_FT_BT,
                cls.EDGE_FT_TP,
                cls.EDGE_LF_BK,
                cls.EDGE_LF_BT,
                cls.EDGE_LF_FT,
                cls.EDGE_LF_TP,
                cls.EDGE_RT_BK,
                cls.EDGE_RT_BT,
                cls.EDGE_RT_FT,
                cls.EDGE_RT_TP,
            }
        )

    @classmethod
    def sides(cls):
        """A set of Dir3's which represent side directions"""
        return frozenset(
            {
                cls.SIDE_RIGHT,
                cls.SIDE_RIGHT,
                cls.SIDE_FRONT,
                cls.SIDE_BACK,
                cls.SIDE_TOP,
                cls.SIDE_BOTTOM,
            }
        )

    @property
    def is_corner(self) -> bool:
        """Does the direction represent a corner?"""
        return self in Dir3.corners()

    @property
    def is_edge(self) -> bool:
        """Does the direction represent an edge?"""
        return self in Dir3.edges()

    @property
    def is_side(self) -> bool:
        """Does the direction represent a side?"""
        return self in Dir3.sides()

    @property
    def is_center(self) -> bool:
        """Does the direction represent a center?"""
        return self == Dir3.CENTER

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

    Useful to specify the AxDir of a stack, or the side of the box, or the z-dir of a `Plane`
    The default X-Y Plane has a z-axis AxDir of AxDir.PLUS_Z.
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
        if (
            x == AxDir.CENTER
            and y == AxDir.CENTER
            and z == AxDir.CENTER
            or x != AxDir.CENTER
            and y != AxDir.CENTER
            and z != AxDir.CENTER
        ):
            raise ValueError("x == CENTER and y == CENTER must be exclusive")
        self.x = x
        self.y = y
        self.z = z

    @property
    def is_x(self):
        return self.x != AxDir.CENTER

    @property
    def is_y(self):
        return self.y != AxDir.CENTER

    @property
    def is_z(self):
        return self.z != AxDir.CENTER

    def __neg__(self) -> AxDir3:
        return AxDir3(-self.x, -self.y, -self.z)

    def to_opposite(self) -> AxDir3:
        return -self

    def to_dir3(self) -> AxDir3:
        return AxDir3(self.x, self.y, self.z)

    def to_z_dir(self) -> tuple[int, int, int]:
        return self.x, self.y, self.z

    def to_x_dir(self) -> tuple[int, int, int]:
        conv: dict[AxDir3, tuple[int, int, int]] = {
            AxDir3.Z_PLUS: (-1, 0, 0),
            AxDir3.Z_MINUS: (1, 0, 0),
            AxDir3.X_PLUS: (1, 0, 0),
            AxDir3.X_MINUS: (-1, 0, 0),
            AxDir3.Y_PLUS: (1, 0, 0),
            AxDir3.Y_MINUS: (-1, 0, 0),
        }
        assert self in conv
        return conv[self]


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

    def side_center(self, side: AxDir3) -> Vec3:
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

        side_bx = Bx.from_edges(left=lf, right=rt, front=fr, back=bk, bottom=bt, top=tp)
        return side_bx.center

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

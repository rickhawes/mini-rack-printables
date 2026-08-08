from enum import Enum, auto
import math
from build123d import (
    Rectangle,
    Vector,
    Circle,
    extrude,
    Face,
    RegularPolygon,
    HexLocations,
    Box,
    Part,
    VectorLike,
)

PLATE_HEX_SPACING = 4.0
PLATE_HEX_WIDTH = 0.5


class PlatePattern(Enum):
    """The type of hole to use for the plate fill."""

    SOLID = auto()
    """No holes, the plate is solid."""
    HEX = auto()
    """Hexagonal holes."""
    CIRCULAR = auto()
    """Circular holes."""


def make_plate(size: VectorLike, pattern: PlatePattern = PlatePattern.SOLID) -> Part:
    """
    Create a cubic plate in the XY plane with Z thickness. Fill with the specified pattern, spacing, and width.

    Args:
        size: The size of the plate in the XY plane.
        pattern: The type of hole to use for the plate fill.

    Returns:
        The plate as a Part object.
    """
    _size = Vector(size)
    if pattern == PlatePattern.SOLID:
        return Box(_size.X, _size.Y, _size.Z)
    elif pattern == PlatePattern.HEX or PlatePattern.CIRCULAR:
        assert _size.X > 2 * PLATE_HEX_SPACING and _size.Y > 2 * PLATE_HEX_SPACING, (
            "Hex plate size must be larger than the hex spacing"
        )
        parimeter = Rectangle(_size.X, _size.Y).wire()
        hole_locs = HexLocations(
            PLATE_HEX_SPACING,
            math.floor(_size.X / (2 * PLATE_HEX_SPACING)),
            math.floor(_size.Y / (2 * PLATE_HEX_SPACING)) - 1,
        )
        if pattern == PlatePattern.HEX:
            holes = hole_locs * RegularPolygon(PLATE_HEX_SPACING - PLATE_HEX_WIDTH, 6).wire()
        elif pattern == PlatePattern.CIRCULAR:
            holes = hole_locs * Circle(PLATE_HEX_SPACING - PLATE_HEX_WIDTH / 2).wire()
        wall_pattern = Face(parimeter, holes)
        return extrude(wall_pattern, amount=_size.Z)
    else:
        raise ValueError(f"Invalid pattern: {pattern}")

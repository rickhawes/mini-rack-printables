"""Classes to generate a fill pattern of holes in a plate.

See Also:
    `Figure` - Main user of holes
"""

import math
from abc import ABC, abstractmethod
from typing import Sequence, override

import build123d as bd

from .geometry import Mm, Rc, Vec2


class HolePattern(ABC):
    """Some figures can support hole patterns"""

    @property
    @abstractmethod
    def inset(self) -> Mm:
        """Return the figure inset used for this pattern"""

    @abstractmethod
    def locations(self, size: Vec2) -> Sequence[bd.Location]:
        """Return the locations of the holes for the given dimensions."""

    @abstractmethod
    def sketch(self) -> bd.Sketch:
        """Sketch a single hole."""


class HexFill(HolePattern):
    """Hexagonal holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        self.spacing = spacing
        self.width = width

    @property
    @override
    def inset(self) -> Mm:
        return self.spacing

    @override
    def locations(self, size: Vec2) -> Sequence[bd.Location]:
        inset = Vec2(self.inset, self.inset)
        cx, cy = (
            math.floor((size - 2 * inset).x / (2 * self.spacing)),
            math.floor(((size - 2 * inset).y - self.spacing) / (2 * self.spacing)),
        )
        return (
            bd.HexLocations(self.spacing, cx, cy).locations if cx > 0 and cy > 0 else []
        )

    @override
    def sketch(self) -> bd.Sketch:
        return bd.RegularPolygon(self.width - self.spacing, 6)


class CircleFill(HolePattern):
    """Circular holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 2.0) -> None:
        self.spacing = spacing
        self.width = width

    @property
    @override
    def inset(self) -> Mm:
        return self.spacing

    @override
    def locations(self, size: Vec2) -> Sequence[bd.Location]:
        inset = Vec2(self.inset, self.inset)
        cx, cy = (
            math.floor((size - 2 * inset).x / (2 * self.spacing)),
            math.floor(((size - 2 * inset).y - self.spacing) / (2 * self.spacing)),
        )
        return (
            bd.HexLocations(self.spacing, cx, cy).locations if cx > 0 and cy > 0 else []
        )

    @override
    def sketch(self) -> bd.Sketch:
        return bd.Circle(self.spacing - self.width / 2)


class SquareFill(HolePattern):
    """Square holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        self.spacing = spacing
        self.width = width

    @property
    @override
    def inset(self) -> Mm:
        return self.spacing

    @override
    def locations(self, size: Vec2) -> Sequence[bd.Location]:
        inset = Vec2(self.inset, self.inset)
        cx, cy = (
            math.floor((size - 2 * inset).x / self.spacing),
            math.floor((size - 2 * inset).y / self.spacing),
        )
        return (
            bd.GridLocations(self.spacing, self.spacing, cx, cy).locations
            if cx > 0 and cy > 0
            else []
        )

    @override
    def sketch(self) -> bd.Sketch:
        return bd.Rectangle(
            width=self.spacing - self.width, height=self.spacing - self.width
        )


def fill_holes(
    base: bd.Sketch,
    base_size: Vec2,
    hole_pattern: HolePattern,
    interior_rc: Rc | None = None,
) -> bd.Sketch:
    """Core algorithm to fill a general outline with a hole pattern.

    Args:
        base (bd.Sketch): The base outline to fill in (must be a single closed curve)
        hole_pattern: The hole pattern to cut into the `base` sketch
        interior_rc: An interior area that can be filled without interfering with
            edges. Used for performance.
    """
    # for this algorithm to work, the base shape must be simple 1 closed-wire shape
    base_wires = base.wires()
    if len(base_wires) != 1 and not base_wires[0].is_closed:
        raise ValueError(
            "The base figure for a WithHolesFigure must be a simple 1-wire figure."
        )

    # seperate the holes that are on the interior
    inset = hole_pattern.inset
    outline = bd.offset(base, amount=-inset) if inset > 0 else base
    hole_locs = hole_pattern.locations(base_size)
    moved_holes = hole_locs * hole_pattern.sketch()
    inside_holes: list[bd.Sketch] = []
    unknown_holes: list[bd.Sketch] = []
    if interior_rc is not None:
        interior_bbox = bd.BoundBox(
            bd.Location(interior_rc.center.to_vector())
            * bd.Rectangle(interior_rc.size.x, interior_rc.size.y)
        )

        for h in moved_holes:
            if interior_bbox.covers(h.bounding_box()):
                inside_holes.append(h)
            else:
                unknown_holes.append(h)
    else:
        unknown_holes = moved_holes

    # holes that overlap the edge work in 2d to calculate the
    # instersections for the parital hole while inside holes
    # work in 1d for peformance
    sk = bd.Sketch()
    if len(unknown_holes) == 0:
        inside_wires = [h.wire() for h in inside_holes]
        sk += bd.Face(base.wire(), inside_wires)
    else:
        sk += base - outline
        sk += outline - (unknown_holes + inside_holes)
    return sk

"""Classes to generate a fill pattern of holes in a plate.

See Also:
    RectangleElement
"""

import math
from abc import ABC, abstractmethod
from typing import override

from build123d import (
    Circle,
    GridLocations,
    HexLocations,
    Rectangle,
    RegularPolygon,
    Sketch,
)
from build123d.build_common import LocationList

from .geometry import Mm, Vec2


class HolePattern(ABC):
    """Some elements can support hole patterns"""

    @abstractmethod
    def locations(self, size: Vec2, inset: Vec2) -> LocationList:
        """Return the locations of the holes for the given dimensions."""

    @abstractmethod
    def sketch(self) -> Sketch:
        """Sketch a single hole."""


class HexFill(HolePattern):
    """Hexagonal holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        self.spacing = spacing
        self.width = width

    @override
    def locations(self, size: Vec2, inset: Vec2) -> LocationList:
        cx, cy = (
            math.floor((size - 2 * inset).x / (2 * self.spacing)),
            math.floor(((size - 2 * inset).y - self.spacing) / (2 * self.spacing)),
        )
        return HexLocations(self.spacing, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    @override
    def sketch(self) -> Sketch:
        return RegularPolygon(self.width - self.spacing, 6)


class CircleFill(HolePattern):
    """Circular holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        self.spacing = spacing
        self.width = width

    @override
    def locations(self, size: Vec2, inset: Vec2) -> LocationList:
        cx, cy = (
            math.floor((size - 2 * inset).x / (2 * self.spacing)),
            math.floor(((size - 2 * inset).y - self.spacing) / (2 * self.spacing)),
        )
        return HexLocations(self.spacing, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    @override
    def sketch(self) -> Sketch:
        return Circle(self.spacing - self.width / 2)


class SquareFill(HolePattern):
    """Square holes for filling a model's surface."""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        self.spacing = spacing
        self.width = width

    @override
    def locations(self, size: Vec2, inset: Vec2) -> LocationList:
        cx, cy = (
            math.floor((size - 2 * inset).x / self.spacing),
            math.floor((size - 2 * inset).y / self.spacing),
        )
        return (
            GridLocations(self.spacing, self.spacing, cx, cy)
            if cx > 0 and cy > 0
            else LocationList([])
        )

    @override
    def sketch(self) -> Sketch:
        return Rectangle(width=self.spacing - self.width, height=self.spacing - self.width)

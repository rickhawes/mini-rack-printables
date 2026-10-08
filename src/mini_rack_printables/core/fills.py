"""
Classes to generate a fill pattern of holes in a plate.
"""

from abc import ABC, abstractmethod
import math
from typing import override
from build123d import (
    Rectangle,
    Circle,
    Sketch,
    HexLocations,
    RegularPolygon,
    GridLocations,
)
from build123d.build_common import LocationList
from .geometry import Mm


class Fill(ABC):
    """Some elements can support fill patterns"""

    spacing: Mm
    width: Mm

    def __init__(self, spacing: Mm, width: Mm) -> None:
        """Initialize with `spacing` between holes and `width` of the fill between holes."""
        self.spacing = spacing
        self.width = width

    @abstractmethod
    def locations(self, dx: Mm, dy: Mm) -> LocationList:
        """Return the locations of the holes for the given dimensions."""
        pass

    @abstractmethod
    def sketch(self) -> Sketch:
        """Sketch a single hole."""
        pass


class HexHoles(Fill):
    """Hexagonal holes for filling a model's surface."""

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        super().__init__(spacing, width)

    @override
    def locations(self, dx: Mm, dy: Mm) -> LocationList:
        cx, cy = (
            math.floor(dx / (2 * self.spacing)),
            math.floor((dy - self.spacing) / (2 * self.spacing)),
        )
        return HexLocations(self.spacing, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    @override
    def sketch(self) -> Sketch:
        return RegularPolygon(self.width - self.spacing, 6)


class CircleHoles(Fill):
    """Circular holes for filling a model's surface."""

    def __init__(self, spacing: Mm = 3.0, width: Mm = 1.5) -> None:
        super().__init__(spacing, width)

    @override
    def locations(self, dx: Mm, dy: Mm) -> LocationList:
        cx, cy = (
            math.floor(dx / (2 * self.spacing)),
            math.floor((dy - self.spacing) / (2 * self.spacing)),
        )
        return HexLocations(self.spacing, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    @override
    def sketch(self) -> Sketch:
        return Circle(self.spacing - self.width / 2)


class SquareHoles(Fill):
    """Square holes for filling a model's surface."""

    def __init__(self, spacing: Mm = 4.0, width: Mm = 1.0) -> None:
        super().__init__(spacing, width)

    @override
    def locations(self, dx: Mm, dy: Mm) -> LocationList:
        cx, cy = math.floor(dx / self.spacing), math.floor(dy / self.spacing)
        return (
            GridLocations(self.spacing, self.spacing, cx, cy)
            if cx > 0 and cy > 0
            else LocationList([])
        )

    @override
    def sketch(self) -> Sketch:
        return Rectangle(width=self.spacing - self.width, height=self.spacing - self.width)

from abc import ABC, abstractmethod
import math
from build123d import (
    Rectangle,
    Circle,
    Sketch,
    HexLocations,
    RegularPolygon,
    GridLocations,
)
from build123d.build_common import LocationList

class Fill(ABC):
    """Some elements can support fill patterns"""

    def __init__(self, spacing, width):
        """Initialize with `spacing` between holes and `width` of the fill between holes."""
        self.s = spacing
        self.w = width

    @abstractmethod
    def locations(self, dx, dy) -> LocationList:
        """Return the locations of the holes for the given dimensions."""
        pass

    @abstractmethod
    def sketch(self) -> Sketch:
        """Sketch a single hole."""
        pass


class HexHoles(Fill):
    """Hexagonal holes for filling a model's surface."""

    def __init__(self, spacing: float = 4.0, width: float = 1.0):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        cx, cy = math.floor(dx / (2 * self.s)), math.floor((dy - self.s) / (2 * self.s))
        return HexLocations(self.s, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    def sketch(self) -> Sketch:
        return RegularPolygon(self.w - self.s, 6)


class CircleHoles(Fill):
    """Circular holes for filling a model's surface."""

    def __init__(self, spacing: float = 3.0, width: float = 1.5):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        cx, cy = math.floor(dx / (2 * self.s)), math.floor((dy - self.s) / (2 * self.s))
        return HexLocations(self.s, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    def sketch(self) -> Sketch:
        return Circle(self.s - self.w / 2)


class SquareHoles(Fill):
    """Square holes for filling a model's surface."""

    def __init__(self, spacing: float = 4.0, width: float = 1.0):
        super().__init__(spacing, width)

    def locations(self, dx, dy) -> LocationList:
        cx, cy = math.floor(dx / self.s), math.floor(dy / self.s)
        return GridLocations(self.s, self.s, cx, cy) if cx > 0 and cy > 0 else LocationList([])

    def sketch(self) -> Sketch:
        return Rectangle(self.s - self.w, self.s - self.w)
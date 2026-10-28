from dataclasses import dataclass
from typing import Self

from build123d import Color, Location, Part, Plane, Solid
from .geometry import Vec2, Vec3

@dataclass
class Piece:
    """The rendered the piece of a model.

    Created by elements and features as the output of rendering. 
    This is a mutabable class which is expected to 

    Attributes:
        part: Part - the build123d Part
        cut: bool - subtract the part instead of the normal add
    """

    part: Part | Solid
    """The part of the model"""
    cut: bool = False
    """Subtract the part, otherwise add the part"""

    def move(self, position: Location | Vec3 | Vec2) -> Self:
        if isinstance(position, Vec2):
            position = Location(position.to_vector())
        elif isinstance(position, Vec3):
            position = Location(position.to_vector())
        _ = self.part.move(position)
        return self

    def set(
        self, color: Color | None = None, label: str | None = None, cut: bool | None = None
    ) -> Self:
        """Set the attributes of the piece"""
        if color is not None:
            self.part.color = color
        if label is not None:
            self.part.label = label
        if cut is not None:
            self.cut = cut
        return self

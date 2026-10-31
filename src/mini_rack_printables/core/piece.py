from dataclasses import dataclass
from typing import Self

from build123d import BoundBox, Color, Location, Part, Plane, Solid, Vector

from .geometry import Vec2, Vec3


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
    _bbox: BoundBox
    """The bounding box of the piece. Used for debugging. """

    def __init__(self, part: Part | Solid, cut: bool = False) -> None:
        self.part = part
        self.cut = cut
        self._bbox = part.bounding_box()

    def moved(self, position: Location | Vec3 | Vec2) -> Piece:
        if isinstance(position, Vec2):
            position = Location(position.to_vector())
        elif isinstance(position, Vec3):
            position = Location(position.to_vector())
        if position != Location((0, 0, 0)):
            moved_part = self.part.moved(position)
            return Piece(moved_part, self.cut)
        else:
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

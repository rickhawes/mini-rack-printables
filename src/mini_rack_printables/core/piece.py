from typing import Self

import build123d as bd

from .geometry import Bx, Vec2, Vec3


class Piece:
    """The rendered the piece of a model.

    Created by block and features as the output of rendering.
    This is a mutable class which is expected to

    Attributes:
        part: Part - the build123d Part
        cut: bool - subtract the part instead of the normal add
    """

    part: bd.Part | bd.Solid
    """The part of the model"""
    cut: bool = False
    """Subtract the part, otherwise add the part"""
    bounds: Bx
    """Bounds of the piece"""
    _bbox: bd.BoundBox
    """The bounding box of the piece. Used for debugging. """

    def __init__(self, part: bd.Part | bd.Solid, cut: bool = False) -> None:
        self.part = part
        self.cut = cut
        bbox = part.bounding_box()
        self._bbox = bbox
        self.bounds = Bx(Vec3.from_vector(bbox.size), Vec3.from_vector(bbox.center()))

    def moved(self, position: bd.Location | Vec3 | Vec2) -> Piece:
        if isinstance(position, Vec2):
            position = bd.Location(position.to_vector())
        elif isinstance(position, Vec3):
            position = bd.Location(position.to_vector())
        if position != bd.Location((0, 0, 0)):
            moved_part = self.part.moved(position)
            return Piece(moved_part, self.cut)
        else:
            return self

    def set(
        self,
        color: bd.Color | None = None,
        label: str | None = None,
        cut: bool | None = None,
    ) -> Self:
        """Set the attributes of the piece"""
        if color is not None:
            self.part.color = color
        if label is not None:
            self.part.label = label
        if cut is not None:
            self.cut = cut
        return self

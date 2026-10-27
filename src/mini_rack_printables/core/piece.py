from dataclasses import dataclass

from build123d import Color, Location, Part, Plane, Solid


@dataclass(frozen=True)
class Piece:
    """The rendered the piece of a model.

    Created by elements and features as the output of rendering.

    Attributes:
        part: Part - the build123d Part
        cut: bool - subtract the part instead of the normal add
    """

    part: Part | Solid
    """The part of the model"""
    cut: bool = False
    """Subtract the part, otherwise add the part"""

    def __mul__(self, other: Location | Plane) -> Piece:
        """Return a piece with a location"""
        return Piece(other * self.part, self.cut)

    def __rmul__(self, other: Location | Plane) -> Piece:
        """Return a piece with a location"""
        return Piece(other * self.part, self.cut)

    def copy(
        self, color: Color | None = None, label: str | None = None, cut: bool | None = None
    ) -> Piece:
        """Add a color to the piece"""
        part = self.part
        if color is not None:
            part.color = color
        if label is not None:
            part.label = label
        new_cut = self.cut if cut is None else cut
        return Piece(part, new_cut)

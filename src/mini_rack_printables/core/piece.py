from dataclasses import dataclass
from build123d import Part


@dataclass(frozen=True)
class Piece:
    """The rendered the piece of model.

    Created by elements and features as the output of rendering

    Attributes:
        part: Part - the build123d Part
        cut: bool - subtract the part instead of the normal add
    """

    part: Part
    """The part of the model"""
    cut: bool = False
    """Subtract the part, otherwise add the part"""

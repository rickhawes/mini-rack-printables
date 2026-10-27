"""
Classes for specifying features of a `Model`. Features may be related to specific devices or general concepts like cutouts.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass
from typing import override

from build123d import Color, Compound, Part, Solid

from .geometry import Bx, Mm, Vec2, Vec3
from .model import Model
from .piece import Piece


class Feature(ABC):
    """
    Base class for all features of a `Model`.
    """

    @dataclass(frozen=True)
    class DesiredSize:
        """
        Represents the desired size of a `ModelPart` on a plate.
        Contains the minimum size and a flag if the feature wants more space than the minimum size.
        """

        min_size: Vec2
        """The minimum size of the plate for rendering."""
        more_x: bool = False
        """Whether the part wants more space than the minimum size."""
        more_y: bool = False
        """Whether the part wants more space than the minimum size."""

    @abstractmethod
    def desired_size(self) -> DesiredSize:
        """
        Return the desired size of plate for rendering.
        The part will always get at least the minimum size of the plate.

        Returns:
            DesiredSize: The minimum size and the expand flag of the plate for rendering.
        """

    @abstractmethod
    def render(self, plate: Bx) -> list[Piece]:
        """
        Render the feature origin at (0, 0) on top of the passed in plate

        Returns:
            A list of pieces representing the solids to be added to the plate.
        """


type FeatureList = Sequence[Sequence[Feature]]
"""A row-column sequence of features."""


@dataclass(frozen=True)
class Rib:
    """
    Represents a rib (width and depth) on a part or shape
    """

    width: Mm
    depth: Mm


class FeatureXRayModel(Model):
    """
    An X-ray model will show the pieces of a Feature without the plate.
    This model is useful for visualizing and debugging the structure of a Feature.
    """

    feature: Feature
    size: Vec3
    only_adds: bool

    def __init__(self, part: Feature, size: Vec3 | None = None, only_adds: bool = True):
        self.feature = part
        self.size = size if size is not None else Vec3(100, 100, 3.5)
        self.only_adds = only_adds

    @override
    def render(self) -> Model.Rendering:
        plate = Bx(self.size, Vec3(0, 0, self.size.z / 2))

        pieces = self.feature.render(plate)
        children: list[Part | Solid] = []
        for piece in pieces:
            if not piece.cut:
                new_piece = piece.copy(color=Color("blue"), label="add")
                children.append(new_piece.part)
            else:
                if not self.only_adds:
                    new_piece = piece.copy(color=Color("red"), label="subtract")
                    children.append(new_piece.part)

        return Model.Rendering(Compound(label="xray", children=children))

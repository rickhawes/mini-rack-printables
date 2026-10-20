"""
Classes for specifying features of a `Model`. Features may be related to specific devices or general concepts like cutouts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .geometry import Mm, Vec2, Vec3
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
    def render(self, plate_size: Vec3 ) -> list[Piece]:
        """
        Render the feature

        Returns:
            A list of PartOutput objects representing the solids to be added to the plate.
        """


type FeatureList = list[list[Feature]]
"""A row-column list of features."""


@dataclass(frozen=True)
class Rib:
    """
    Represents a rib (width and depth) on a part or shape
    """

    width: Mm
    depth: Mm

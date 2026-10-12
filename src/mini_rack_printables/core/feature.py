"""
Classes for specifying features of a `Model`. Features may be related to specific devices or general concepts like cutouts.
"""

from build123d import Solid, Part
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .geometry import Bx, Vec2, Mm


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
        pass

    @abstractmethod
    def render(self, base_plate: Bx) -> list[FeaturePiece]:
        """
        Render the feature

        Returns:
            A list of PartOutput objects representing the solids to be added to the plate.
        """
        pass


type FeatureList = list[Feature] | list[list[Feature]]
"""A row-column list of features."""


@dataclass(frozen=True)
class FeaturePiece:
    """
    Represents the output of rendering a `ModelFeature`, containing the solid and
    the add mode (i.e. location and combination mode).

    Attributes:
        part: The solid for the part located by the part
        subtract: Mode of the solid's addition (i.e. SUBTRACT, ADD)
    """

    part: Solid | Part
    subtract: bool = False


@dataclass(frozen=True)
class Rib:
    """
    Represents a rib (width and depth) on a part or shape
    """

    width: Mm
    depth: Mm

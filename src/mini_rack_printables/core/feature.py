"""
Classes for specifying features of a `Model`. Features may be related to specific
devices or general concepts like cutouts.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass

from .assembler import Assembler
from .geometry import Mm, Vec2


class Feature(ABC):
    """
    Base class for all features of a `Model`.
    """

    @dataclass(frozen=True)
    class DesiredSize:
        """
        Represents the desired size of a `ModelPart` on a plate.
        Contains the minimum size and a flag if the feature wants more space than the
        minimum size.
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
            DesiredSize: The minimum size and the expand flag of the plate for
                rendering.
        """

    @abstractmethod
    def render(self, asm: Assembler) -> None:
        """
        Render the feature into the passed in Assembler.

        Args:
            asm (Assembler): The Assembler receives the pieces of the feature
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

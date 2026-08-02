from abc import ABC, abstractmethod
from build123d.topology.composite import Part, Vector
from dataclasses import dataclass


@dataclass
class FeatureParts:
    addition: Part | None
    subtraction: Part | None


class ModelFeature(ABC):
    """
    Base class for all Model features
    """

    @abstractmethod
    def render(self, plate_size: Vector) -> FeatureParts:
        """
        Render the feature

        Returns:
            A tuple with a part for substracting from the plate and a part to add to the plate top.
        """
        pass

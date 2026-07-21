from abc import ABC, abstractmethod
from build123d.topology.composite import Compound



class Model(ABC):
    """
    Base class for all 3d printable models.
    """

    @abstractmethod
    def render(self) -> Compound:
        """
        Render the model as a shape

        Returns:
            A shape
        """
        pass

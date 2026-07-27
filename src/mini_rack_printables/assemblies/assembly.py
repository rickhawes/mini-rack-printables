from abc import ABC, abstractmethod

from solid2.core.object_base import ObjectBase


class Assembly(ABC):
    """
    Base class for all assemblies.
    """

    @abstractmethod
    def render(self) -> ObjectBase:
        """
        Render the assembly

        Returns:
                OpenSCAD object
        """
        pass

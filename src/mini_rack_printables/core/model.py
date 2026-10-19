"""Classes to model a 3D printable"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

import ocp_vscode as viewer
from build123d import Part, export_step


class Model(ABC):
    """Base-class for 3d printable models.

    Every printing project has a `Model` and a `Modeler` instance. The model is a
    subclass of the `Model` base-class and while `Modeler` is instance of this class.

    See Also:
        `Modeler` - the companion class needed to render a model

    """

    @dataclass(frozen=True)
    class Rendering:
        """The rendering of a model and the operations that can be performed"""

        part: Part

        def show(self) -> None:
            viewer.show(self.part)

        def export(self, filename: str) -> None:
            export_step(self.part, filename)

    @abstractmethod
    def render(self) -> Rendering:
        """
        Render the model in a Rendering class.
        """

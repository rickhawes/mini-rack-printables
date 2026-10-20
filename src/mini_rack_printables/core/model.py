"""Classes to model a 3D printable"""
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import final

import ocp_vscode as viewer
from build123d import Part, export_step, Compound


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
            if not export_step(self.part, filename):
                raise IOError("File not saved")

    @abstractmethod
    def render(self) -> Rendering:
        """
        Render the model in a Rendering class.
        """

@final
class ModelLogger:
    """Class to log a 3d printable models so they can be displayed.

    TODO: Rethink with Pieces
    """

    @final
    class LogEntry:
        def __init__(self, group_name: str, function_name: str, part: Compound | Part) -> None:
            self.group_name = group_name
            self.function_name = function_name
            self.part = part
            self.size = part.bounding_box().size

    entries: dict[str, list[LogEntry]] = {}

    def log(self, part: Compound | Part, group: str | None = None) -> None:
        frame = sys._getframe(1)
        assert frame is not None
        group_name = group if group is not None else frame.f_globals["__name__"]
        function_name = frame.f_code.co_name
        entry = ModelLogger.LogEntry(group_name, function_name, part)
        if group_name not in self.entries:
            self.entries[group_name] = []
        self.entries[group_name].append(entry)

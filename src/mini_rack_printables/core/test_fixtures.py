"""
Common test fixtures defined in core to be in the import path for tests.
"""

import sys
from dataclasses import dataclass
from enum import Enum, auto

import build123d as bd

from .assembler import Assembler
from .feature import Feature
from .geometry import AxDir3, Bx, Vec3
from .rendering import Rendering


# pylint: disable=too-few-public-methods
class TestLogger:
    """Class to log a 3d printable models so they can be displayed with viewer.

    This logger is useful in testing, pytest in particular.
    Part of the core package to allow it to be included in tests.
    """

    type LogableType = bd.Part | bd.Compound | bd.Sketch

    @dataclass(init=False)
    class LogEntry:
        """Entry for the log."""

        group_name: str
        function_name: str
        part: TestLogger.LogableType
        size: Vec3

        def __init__(
            self, group_name: str, function_name: str, part: TestLogger.LogableType
        ) -> None:
            self.group_name = group_name
            self.function_name = function_name
            self.part = part
            self.size = Vec3.from_vector(part.bounding_box().size)

    entries: dict[str, list[LogEntry]] = {}

    def log(
        self, part: TestLogger.LogableType | Rendering, group: str | None = None
    ) -> None:
        """Log a part into the logger"""
        # pylint: disable=protected-access
        frame = sys._getframe(1)
        assert frame is not None
        group_name = group if group is not None else frame.f_globals["__name__"]
        function_name = frame.f_code.co_name
        if isinstance(part, Rendering):
            part = part.part
        entry = TestLogger.LogEntry(group_name, function_name, part)
        if group_name not in self.entries:
            self.entries[group_name] = []
        self.entries[group_name].append(entry)


STD_PLATE_SIZE = Vec3(100, 100, 5)
"""Standard plate for tests and examples"""


class XRayShow(Enum):
    """Parameter for `feature_xray`."""

    ALL = auto()
    """Show both adds and cuts"""
    ONLY_ADDS = auto()
    """Show only adds"""
    ONLY_CUTS = auto()
    """Show only cuts"""


def feature_xray(
    feature: Feature, plate_size: Vec3 = STD_PLATE_SIZE, show: XRayShow = XRayShow.ALL
) -> Rendering:
    """Render the feature with an invisible plate.

    Adds are colored blue and subtracts are colored .

    Args:
        feature (Feature): The feature to render.
        plate_size (Vec3): The plate_size to pass to the feature's render method.
        show (XRayShow): Show adds or cuts
    """

    plate = Bx(plate_size, Vec3(0, 0, plate_size.z / 2))
    asm = Assembler.make(plate, z_dir=AxDir3.TOP)

    feature.render(asm)
    children: list[bd.Part | bd.Solid] = []
    for piece in asm.all_pieces():
        if not piece.cut:
            if show in [XRayShow.ONLY_ADDS, XRayShow.ALL]:
                new_piece = piece.set(color=bd.Color("blue"), label="add")
                children.append(new_piece.part)
        else:
            if show in [XRayShow.ONLY_CUTS, XRayShow.ALL]:
                new_piece = piece.set(color=bd.Color("red"), label="subtract")
                children.append(new_piece.part)

    return Rendering(bd.Compound(label="xray", children=children))

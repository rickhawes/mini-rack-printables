"""
Fixture to display on OCP Viewer the output of each test
"""

import pytest
import sys
from ocp_vscode import push_object, show_objects, reset_show, Camera
from build123d import Compound, Part, Location, Text, Sketch, Rectangle, Align, Color


STD_SPACING = 80
MIN_SPACING = 10
TEXT_BOX_HEIGHT = 10


class Logger:
    class LogEntry:
        def __init__(self, group_name: str, function_name: str, part: Compound | Part):
            self.group_name = group_name
            self.function_name = function_name
            self.part = part
            self.size = part.bounding_box().size

    entries: dict[str, list[LogEntry]] = {}

    def log(self, part: Compound | Part, group: str | None = None):
        frame = sys._getframe(1)  # Get the caller's frame
        assert frame is not None
        group_name = group if group is not None else frame.f_globals["__name__"]
        function_name = frame.f_code.co_name
        entry = Logger.LogEntry(group_name, function_name, part)
        if group_name not in self.entries:
            self.entries[group_name] = []
        self.entries[group_name].append(entry)


@pytest.fixture(scope="session")
def viewer_logger():
    # Start of the session
    logger = Logger()
    yield logger

    # End of the session
    reset_show()

    def Label(text: str) -> Sketch:
        label = Rectangle(STD_SPACING - 10, TEXT_BOX_HEIGHT)
        label -= Text(text, font_size=4, align=(Align.CENTER, Align.CENTER))
        sk = Sketch(label)
        sk.color = Color("white")
        return sk

    # Layout by module and function
    x, y = 0, 0
    for group_name, entries in logger.entries.items():
        # A group label
        group_label = Location((-STD_SPACING - 10, y, 0)) * Label(group_name)
        push_object(group_label, name=group_name)
        x = 0

        # A group of entries
        for entry in entries:
            c = Location((x, y, 0)) * Compound(
                label=entry.function_name,
                children=[
                    entry.part,
                    Location((0, -STD_SPACING / 2 + TEXT_BOX_HEIGHT / 2, 0))
                    * Label(entry.function_name),
                ],
            )
            push_object(c, name=entry.function_name)
            x += STD_SPACING if entry.size.X < STD_SPACING else entry.size.X + MIN_SPACING
        y += STD_SPACING
    show_objects(reset_camera=Camera.TOP)
    #

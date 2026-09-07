"""
Fixture to display on OCP Viewer the output of each test
"""

import pytest
import sys
from ocp_vscode import push_object, show_objects, reset_show, Camera
from build123d import Compound, Part, Location, Text, Sketch, Rectangle, Align, Color

SPACING = 80
TEXT_BOX_HEIGHT = 10


class Logger:
    class LogEntry:
        def __init__(self, group_name: str, function_name: str, part: Compound | Part):
            self.group_name = group_name
            self.function_name = function_name
            self.part = part

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
        label = Rectangle(SPACING - 10, TEXT_BOX_HEIGHT)
        label -= Text(text, font_size=4, align=(Align.CENTER, Align.CENTER))
        sk = Sketch(label)
        sk.color = Color("white")
        return sk

    # Layout by module and function
    for row, (group_name, entries) in enumerate(logger.entries.items()):
        # A group label
        group_label = Location((-SPACING - 10, row * SPACING, 0)) * Label(group_name)
        push_object(group_label, name=group_name)

        # A group of entries
        for col, entry in enumerate(entries):
            c = Location((col * SPACING, row * SPACING, 0)) * Compound(
                label=entry.function_name,
                children=[
                    entry.part,
                    Location((0, -SPACING / 2 + TEXT_BOX_HEIGHT / 2, 0))
                    * Label(entry.function_name),
                ],
            )
            push_object(c, name=entry.function_name)
    show_objects(reset_camera=Camera.TOP)
    #

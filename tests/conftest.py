"""
Fixture to display on OCP Viewer the output of each test
"""

from collections.abc import Generator
from mini_rack_printables import ModelLogger

import pytest
from build123d import Align, Color, Compound, Location, Rectangle, Sketch, Text
from ocp_vscode import Camera, push_object, reset_show, show_objects

STD_SPACING = 80
MIN_SPACING = 10
TEXT_BOX_HEIGHT = 10
MAX_ELEMENTS_PER_ROW = 6



@pytest.fixture(scope="session")
def viewer_logger()-> Generator[ModelLogger, None, None]:
    # Start of the session
    logger = ModelLogger()
    yield logger

    # End of the session
    reset_show()

    def label(text: str) -> Sketch:
        rect = Rectangle(STD_SPACING - 10, TEXT_BOX_HEIGHT)
        rect -= Text(text, font_size=4, align=(Align.CENTER, Align.CENTER))
        sk = Sketch(rect)
        sk.color = Color("white")
        return sk

    # Layout by module and function
    x, y = 0, 0
    for group_name, entries in logger.entries.items():
        # A group label
        group_label = Location((-STD_SPACING - 10, y, 0)) * label(group_name)
        push_object(group_label, name=group_name)

        row = 0
        for i in range(0, len(entries), MAX_ELEMENTS_PER_ROW):
            x = 0
            for entry in entries[i : i + MAX_ELEMENTS_PER_ROW]:
                c = Location((x, y, 0)) * Compound(
                    label=entry.function_name,
                    children=[
                        entry.part,
                        Location((0, -STD_SPACING / 2 + TEXT_BOX_HEIGHT / 2, 0))
                        * label(entry.function_name),
                    ],
                )
                push_object(c, name=entry.function_name)
                x += STD_SPACING if entry.size.X < STD_SPACING else entry.size.X + MIN_SPACING
            y -= STD_SPACING
            row += 1
    _ = show_objects(reset_camera=Camera.TOP)  # pyright: ignore[reportUnknownVariableType]


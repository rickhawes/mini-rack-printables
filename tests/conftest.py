"""
Fixture to display on OCP Viewer the output of each test

TODO:
    - Make tests use standard sizes instead of 60
"""

from collections.abc import Generator

import build123d as bd
import pytest
from ocp_vscode import Camera, push_object, reset_show, show_objects

from mini_rack_printables import TestLogger

STD_SPACING = 80
MIN_SPACING = 10
TEXT_BOX_HEIGHT = 10
MAX_ELEMENTS_PER_ROW = 6


@pytest.fixture(scope="session")
def viewer_logger() -> Generator[TestLogger, None, None]:
    # Start of the session
    logger = TestLogger()
    yield logger

    # End of the session
    reset_show()

    def label(text: str) -> bd.Sketch:
        rect = bd.Rectangle(STD_SPACING - 10, TEXT_BOX_HEIGHT)
        rect -= bd.Text(text, font_size=4, align=(bd.Align.CENTER, bd.Align.CENTER))
        sk = bd.Sketch(rect)
        sk.color = bd.Color("white")
        return sk

    # Layout by module and function
    x, y = 0, 0
    for group_name, entries in logger.entries.items():
        # A group label
        group_label = bd.Location((-STD_SPACING - 10, y, 0)) * label(group_name)
        push_object(group_label, name=group_name)

        row = 0
        for i in range(0, len(entries), MAX_ELEMENTS_PER_ROW):
            x = 0
            for entry in entries[i : i + MAX_ELEMENTS_PER_ROW]:
                c = bd.Location((x, y, 0)) * bd.Compound(
                    label=entry.function_name,
                    children=[
                        entry.part,
                        bd.Location((0, -STD_SPACING / 2 + TEXT_BOX_HEIGHT / 2, 0))
                        * label(entry.function_name),
                    ],
                )
                push_object(c, name=entry.function_name)
                x += (
                    STD_SPACING
                    if entry.size.x < STD_SPACING
                    else entry.size.x + MIN_SPACING
                )
            y -= STD_SPACING
            row += 1
    _ = show_objects(reset_camera=Camera.TOP)

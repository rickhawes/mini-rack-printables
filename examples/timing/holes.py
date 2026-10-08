"""
Compare the use of builder vs algebra mode for drawing 25x25 grid of holes in a rectangle
"""

import timeit

from build123d import *

major_r = 10


def algebra_mode():
    # 1. Calculate hole locations (e.g., 625 holes in a hex grid)
    hole_locs = HexLocations(major_r, 25, 25)

    # 2. Create wires for the perimeter and individual hole shapes
    face_perimeter = Rectangle(500, 600).wire()
    hex_hole = RegularPolygon(major_r - 1, 6, major_radius=True).wire()
    holes = hole_locs * hex_hole

    # 3. Create a single Face containing the perimeter and all cutouts
    grid_pattern = Face(face_perimeter, holes)

    # 4. Extrude once into a 3D solid
    _ = extrude(grid_pattern, 1)


algebra_start = timeit.default_timer()
algebra_mode()
print(f"Algebra Time: {timeit.default_timer() - algebra_start:0.3f}s")


def builder_mode():
    with BuildPart() as grid_part:
        with BuildSketch() as sketch:
            Rectangle(500, 600)
            with HexLocations(major_r, 25, 25):
                RegularPolygon(major_r - 1, 6, mode=Mode.SUBTRACT)
        extrude(amount=1)
    _ = grid_part.part


builder_start = timeit.default_timer()
builder_mode()
print(f"Builder Time: {timeit.default_timer() - builder_start:0.3f}s")

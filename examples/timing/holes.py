"""
Compare the use of builder vs algebra mode for drawing 25x25 grid of
holes in a rectangle in build123d
"""

import timeit

import build123d as bd

MAJOR_R = 10


def algebra_mode() -> None:
    """Draw in using algebra mode"""
    # 1. Calculate hole locations (e.g., 625 holes in a hex grid)
    hole_locs = bd.HexLocations(MAJOR_R, 25, 25)

    # 2. Create wires for the perimeter and individual hole shapes
    face_perimeter = bd.Rectangle(500, 600).wire()
    hex_hole = bd.RegularPolygon(MAJOR_R - 1, 6, major_radius=True).wire()
    holes = hole_locs * hex_hole

    # 3. Create a single Face containing the perimeter and all cutouts
    grid_pattern = bd.Face(face_perimeter, holes)

    # 4. Extrude once into a 3D solid
    _ = bd.extrude(grid_pattern, 1)


algebra_start = timeit.default_timer()
algebra_mode()
print(f"Algebra Time: {timeit.default_timer() - algebra_start:0.3f}s")


def builder_mode() -> None:
    """Draw using builders."""
    with bd.BuildPart() as grid_part:
        with bd.BuildSketch():
            _ = bd.Rectangle(500, 600)
            with bd.HexLocations(MAJOR_R, 25, 25):
                _ = bd.RegularPolygon(MAJOR_R - 1, 6, mode=bd.Mode.SUBTRACT)
        _ = bd.extrude(amount=1)
    _ = grid_part.part


builder_start = timeit.default_timer()
builder_mode()
print(f"Builder Time: {timeit.default_timer() - builder_start:0.3f}s")

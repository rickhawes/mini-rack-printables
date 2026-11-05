"""
In algebra mode, compare use of fuse of single object versus a
fuse of a list of object in build123d
"""

import timeit

import build123d as bd


def fuse_each_object() -> None:
    """Fuse at each object."""
    diam = 80
    holes = bd.Sketch()
    r = bd.Rectangle(2, 2)
    for loc in bd.GridLocations(4, 4, 20, 20):
        if loc.position.X**2 + loc.position.Y**2 < (diam / 2 - 1.8) ** 2:
            # fusing called with the += overload
            holes += loc * r

    # fusing using the - overload
    _ = bd.Circle(diam / 2) - holes


each_object_start = timeit.default_timer()
fuse_each_object()
print(f"Fuse each object time: {timeit.default_timer() - each_object_start:0.3f}s")


def fuse_once() -> None:
    """Fuse the parts together once."""
    diam = 80
    r = bd.Rectangle(2, 2)
    holes = [
        loc * r
        for loc in bd.GridLocations(4, 4, 20, 20).locations
        if loc.position.X**2 + loc.position.Y**2 < (diam / 2 - 1.8) ** 2
    ]

    # fuse called the subtract overload
    _ = bd.Circle(diam / 2) - holes


once_start = timeit.default_timer()
fuse_once()
print(f"Fuse once time: {timeit.default_timer() - once_start:0.3f}s")

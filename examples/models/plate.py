"""Make a plate with holes using an Assembler."""

from mini_rack_printables import (
    Assembler,
    BoxBlock,
    CylinderBlock,
    ExtrudedBlock,
    SlotFigure,
    Vec2,
    Vec3,
)

size = Vec3(100, 100, 5)


def hole_centers() -> list[Vec2]:
    """A list of holes to holes"""
    dx = size.x / 2 - 10
    dy = size.y / 2 - 10
    return [Vec2(x, y) for x in [dx, -dx] for y in [dy, 0, -dy]]


def stand_centers() -> list[Vec2]:
    """A list of stand locations."""
    return [Vec2(x, y) for x in [-10, 10] for y in [0]]


base = BoxBlock(size.x, size.y, size.z)
hole = ExtrudedBlock(SlotFigure(10, 5), size.z)
stand = CylinderBlock(5, 10)

# Assembler is used to assemble this model
asm = Assembler.make_with_block(base)
cutout_asm = asm.make_cutout_sub()
# made with top side as the plane
asm.place_block(stand, [Assembler.Place(offset=p) for p in stand_centers()])

# place the holes on the base using the cut mode
cutout_asm.place_block(hole, [Assembler.Place(offset=p) for p in hole_centers()])

rendering = asm.make_rendering()
rendering.show()

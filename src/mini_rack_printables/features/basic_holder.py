"""A extruded rectangle ring, a basis building block for holders."""

from dataclasses import dataclass

from mini_rack_printables import HolePattern

from ..core.assembler import Assembler
from ..core.block import ExtrudedBlock, PlateBlock
from ..core.corners import InsetCorners
from ..core.figures import CutoutFigure, RectangleFigure
from ..core.geometry import AxDir3, Mm, Vec2, Vec3
from ..core.hole_patterns import HexFill


@dataclass(frozen=True)
class BasicHolderStyle:
    """
    The sytle of the holder.
    """

    outer_radius: Mm = 0.0
    """The outer radius of the corner."""
    inner_radius: Mm = 0.0
    """The inner radius of the corner. """
    wall_thickness: Mm = 2.5
    """The wall's thickness."""
    corner_edge: Mm = 1.0
    """The corner's solid part"""
    holes: HolePattern | None = HexFill()
    """The hole pattern for the wall"""


def build_basic_holder(
    asm: Assembler, device_size: Vec3, style: BasicHolderStyle = BasicHolderStyle()
) -> None:
    """Assemble a basic holder with rounded corners and hole pattern."""
    # geometry
    dx, dy, dz = device_size.to_tuple()
    cr = style.outer_radius
    w = style.wall_thickness
    ir = style.inner_radius
    dc = ir + style.corner_edge  # corner width

    # add corners
    corners = ExtrudedBlock(
        CutoutFigure(
            base=CutoutFigure(
                RectangleFigure(dx + 2 * w, dy + 2 * w, cr), RectangleFigure(dx, dy, ir)
            ),
            cutout=RectangleFigure(dx + 2 * w, dy + 2 * w, InsetCorners(dc + w)),
        ),
        dz,
    )
    asm.place_block(corners)

    # add walls
    # build around a box defined by the device
    device_bx = asm.place_bounds(size=device_size)
    for side in [AxDir3.X_PLUS, AxDir3.X_MINUS, AxDir3.Y_PLUS, AxDir3.Y_MINUS]:
        size = device_bx.side_size(side) - Vec2(2 * dc, 0)
        block = PlateBlock(size.x, size.y, w, holes=style.holes)
        asm.make_sub(device_bx, side).place_block(block)

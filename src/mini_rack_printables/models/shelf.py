from dataclasses import dataclass
from typing import ClassVar, final, override

from mini_rack_printables.core.layouts import GridLayout

from ..core.assembler import Assembler
from ..core.block import ExtrudedBlock, PlateBlock
from ..core.corners import SquareCorners
from ..core.feature import FeatureList
from ..core.figures import (
    AlignedFigure,
    CutoutFigure,
    RectangleFigure,
    RotatedFigure,
    TrapezoidFigure,
)
from ..core.geometry import Ax2, AxDir, AxDir3, Bx, Mm, Vec3
from ..core.layouts import Layout
from ..core.rendering import Rendering
from .rack_dims import RackDims, ShelfTabDims, rack_units_to_mm
from .rack_holes import RackHolePattern


@dataclass(frozen=True)
class ShelfStyle:
    """
    Parameters for the style of the rack shelf.
    """

    base_thickness: Mm = 4.0
    """Thickness of the base of the rack shelf."""
    wall_thickness: Mm = 3.0
    """Thickness of the wall of the rack shelf."""
    face_thickness: Mm = 3.0
    """Thickness of the face of the rack shelf."""
    face_rounding: Mm = 3.0
    """Rounding of the face of the rack shelf."""
    shelf_depth: Mm = RackDims.DEPTH_8INCH
    """Whether the rack shelf has a ten inch depth."""
    shelf_back_depth: float = 20
    """The back of the shelf has a small inset."""
    open_face: bool = True
    """Whether the face of the rack shelf is open or closed."""
    middle_holes: bool = True
    """Whether the rack shelf plate has middle holes."""
    half_height_bottom: bool = False
    """Whether the rack shelf plate has half-height bottom holes."""

    OPEN_FACE: ClassVar["ShelfStyle"]
    """A rack shelf with an open face."""

    CLOSE_FACE: ClassVar["ShelfStyle"]
    """A rack shelf with a closed face."""


ShelfStyle.OPEN_FACE = ShelfStyle(open_face=True)
ShelfStyle.CLOSE_FACE = ShelfStyle(open_face=False)


def shelf(
    rack_units: float = 1.0,
    style: ShelfStyle = ShelfStyle.OPEN_FACE,
    features: FeatureList | None = None,
    layout: Layout | None = None,
) -> Rendering:
    """Render a rack shelf

    Args:
        rack_units (float): The number of rack units the shelf spans.
        style (ShelfStyle): The style of the rack shelf.
        features (FeatureList): The features to add to the rack shelf.
        layout (Layout): The layout of the rack shelf. Default is GridLayout.

    Returns:
        Rendering of a rack shelf.
    """
    if features is not None and layout is None:
        layout = GridLayout()

    # geometry
    plate_size = Vec3(
        RackDims.SHELF_WIDTH,
        style.shelf_depth,
        style.base_thickness,
    )
    exterior_dz = rack_units_to_mm(rack_units)
    exterior_bx = Bx(plate_size.x, plate_size.y, exterior_dz, 0, 0, exterior_dz / 2)
    interior_dz = rack_units_to_mm(rack_units) - plate_size.z
    interior_dx = plate_size.x - 2 * style.wall_thickness
    interior_bx = Bx(interior_dx, plate_size.y, interior_dz, 0, 0, interior_dz / 2)

    # wall
    def build_walls() -> None:
        # Make a wall block that is a combination of figures
        wall_size = Vec3(plate_size.y, interior_dz, style.wall_thickness)
        shelf_back = style.shelf_back_depth
        wall_back = RectangleFigure(shelf_back, 2 * plate_size.z)
        wall_trap = TrapezoidFigure(
            wall_size.y,
            wall_size.x / 2 - shelf_back,
            angle1=90,
            angle2=TrapezoidFigure.angle_from_widths(
                wall_size.y, 2 * plate_size.z, wall_size.x / 2 - shelf_back, angle1=90
            ),
        )
        wall_trap = RotatedFigure(wall_trap, angle=90)
        wall_holes = RectangleFigure(
            wall_size.x / 2,
            wall_size.y,
            corners=SquareCorners(wall_size.z),  # insets the fill area a bit
        )
        wall_figure = AlignedFigure(
            [wall_back, wall_trap, wall_holes], Ax2.X, AxDir.MINUS
        )
        wall = ExtrudedBlock(wall_figure, wall_size.z)

        # Place the walls on the plate
        wall_plate_bx_minus = interior_bx.side_bx(AxDir3.X_MINUS)
        wall_plate_bx_plus = wall_plate_bx_minus.move(
            Vec3(interior_bx.size.x + wall_size.z, 0, 0)
        )
        for plate_bx in [wall_plate_bx_minus, wall_plate_bx_plus]:
            wall_sub = plate_asm.make_sub(plate_bx, AxDir3.X_MINUS)
            wall_sub.place_block(wall)

    # add face
    def build_faceplate(base_asm: Assembler) -> None:
        size = Vec3(RackDims.WIDTH_10INCH, exterior_dz, style.face_thickness)
        holes = RackHolePattern(rack_units)
        figure = RectangleFigure(
            size.x, size.y, corners=style.face_rounding, holes=holes
        )
        if style.open_face:
            open_dx = ShelfTabDims.MAX_DX_TABS - 2 * style.wall_thickness
            figure = CutoutFigure(figure, RectangleFigure(open_dx, size.y))
        face = ExtrudedBlock(figure, size.z)
        sub = base_asm.make_sub(exterior_bx, AxDir3.Y_MINUS)
        sub.place_block(face)

    # shelf
    asm = Assembler.make(exterior_bx.side_bx(AxDir3.BOTTOM))
    build_faceplate(asm)
    plate = PlateBlock(plate_size.x, plate_size.y, plate_size.z)
    plate_asm = asm.stack_block(plate)
    build_walls()
    build_faceplate(asm)
    if features is not None:
        assert layout is not None
        layout.render_features(features, asm)

    return asm.make_rendering()

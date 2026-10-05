from dataclasses import dataclass
from typing import final, override

from build123d import (
    BuildSketch,
    BuildPart,
    Plane,
    Compound,
    RectangleRounded,
    Trapezoid,
    Location,
    mirror,
    extrude,
    Mode,
    Axis,
    add,
)

from ..dimensions import RackDims, ShelfTabDims
from ..holes import sketch_rack_holes
from ..geometry import Rib, Bx, Vec3, Mm
from .model import Model
from ..parts.model_part import PlatePlanes, PartList
from ..parts.layouts import PartLayout, RowLayout


@final
class FacePlate(Model):
    """
    A faceplate model with a height and `style`. Parts can be added as well.
    """

    @dataclass(frozen=True)
    class Style:
        """Style parameters for the faceplate"""

        thickness: Mm = 3.0
        """Thickness of the plate"""
        rounding: Mm = 3.0
        """Rounding applied to corners of a face_plate"""
        middle_holes: bool = True
        """Draw middle screw holes"""
        half_height_bottom: bool = False
        """Start the bottom with a half unit"""
        rib: Rib = Rib(2.0, 1.0)
        """Rib size for the plate"""

    STD_RIB = Rib(2.0, 1.0)
    """Standard rib size"""

    NO_RIB = Rib(0, 0)
    """No rib size"""

    STD_WITH_RIB = Style(rib=Rib(2.0, 1.0))
    """Standard style with rib"""

    PLAIN = Style(rib=Rib(0, 0))
    """Standard style without rib"""

    rack_units: float
    """Rack units of the plate"""
    style: Style
    parts: PartList | None = None
    layout: PartLayout = RowLayout()

    def __init__(
        self,
        rack_units: float,
        style: Style = Style(),
        parts: PartList | None = None,
        layout: PartLayout = RowLayout(),
    ) -> None:
        """
        Create a faceplate model

        Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            style: Style options for the plate
            parts: The feature to use for the plate. Defaults to None.
        """
        self.rack_units = rack_units
        self.style = style
        self.parts = parts
        self.layout = layout

    @override
    def render(self) -> Compound:
        """
        Render the faceplate

        Returns:
            A compound shape of the faceplate.
        """
        plate_size = Vec3(
            RackDims.WIDTH_10INCH, self.rack_units * RackDims.HEIGHT_1U, self.style.thickness
        )
        part_area_size = Vec3(
            ShelfTabDims.MAX_DX_TABS,
            plate_size.y - 2 * self.style.rib.width,
            self.style.thickness,
        )

        with BuildPart() as face_plate:
            # baseplate
            with BuildSketch():
                # plate
                _ = RectangleRounded(plate_size.x, plate_size.y, self.style.rounding)
                # screw holes
                holes = sketch_rack_holes(
                    self.rack_units, self.style.middle_holes, self.style.half_height_bottom
                )
                _ = add(holes, mode=Mode.SUBTRACT)
            _ = extrude(amount=plate_size.z)

            # ribs
            if self.style.rib.width > 0:
                with BuildPart() as rib:
                    # orient the extrusion to point in the Y-Axis
                    side_plane = (
                        Plane(face_plate.faces().sort_by(Axis.Y)[0])
                        .rotated((180, 180, 0))
                        .moved(Location((0, (plate_size.z + self.style.rib.depth) / 2, 0)))
                    )
                    with BuildSketch(side_plane):
                        _ = Trapezoid(part_area_size.x, self.style.rib.depth, 30)
                    _ = extrude(amount=self.style.rib.width)
                _ = mirror(rib.part, Plane.XZ)  # place on both sides

        # Add/subtract parts
        result = face_plate.part
        assert result is not None
        if self.parts:
            part_planes = PlatePlanes(
                Bx(size=part_area_size, shift=Vec3(0, 0, part_area_size.z / 2))
            )
            pieces = PartLayout.render_pieces(self.parts, part_planes, self.layout)
            result = PartLayout.assemble_pieces(result, pieces)

        return Compound(label="face_plate", children=[result])

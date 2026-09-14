from dataclasses import dataclass
from build123d import (
    BuildSketch,
    BuildPart,
    Vector,
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
from ..rack_holes import sketch_rack_holes
from ..geometry import Rib
from .model import Model
from ..parts.model_part import ModelPart, Plate


class FacePlate(Model):
    """
    A face plate model
    """

    @dataclass
    class Style:
        """Style parameters for the face plate"""

        thickness: float = 3.0
        """Thickness of the plate"""
        rounding: float = 3.0
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

    def __init__(
        self,
        rack_units: float,
        style: Style = Style(),
        part: ModelPart | None = None,
    ):
        """
        Create a face plate model

        Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            style: Style options for the plate
            part: The feature to use for the plate. Defaults to None.
        """
        self.rack_units = rack_units
        self.style = style
        self.part = part

    def render(self) -> Compound:
        """
        Render the face plate

        Returns:
            A compound shape of the face plate.
        """
        plate_size = Vector(
            RackDims.WIDTH_10INCH, self.rack_units * RackDims.HEIGHT_1U, self.style.thickness
        )
        part_area_size = Vector(
            plate_size.X - 2 * ShelfTabDims.WIDTH_TECMOJO - 2 * self.style.rib.width,
            plate_size.Y - 2 * self.style.rib.width,
            self.style.thickness,
        )
        plate = Plate(
            part_area_size,
            Plane(origin=Vector(0, 0, plate_size.Z)),
            Plane(origin=Vector(0, 0, 0)),
        )

        with BuildPart() as face_plate:
            # base plate
            with BuildSketch():
                # plate
                RectangleRounded(plate_size.X, plate_size.Y, self.style.rounding)

                # screw holes
                add(
                    sketch_rack_holes(
                        self.rack_units, self.style.middle_holes, self.style.half_height_bottom
                    ),
                    mode=Mode.SUBTRACT,
                )
            extrude(amount=plate_size.Z)

            # ribs
            if self.style.rib.width > 0:
                with BuildPart() as rib:
                    # orient the extrusion to point in the Y-Axis
                    side_plane = (
                        Plane(face_plate.faces().sort_by(Axis.Y)[0])
                        .rotated((180, 180, 0))
                        .moved(Location((0, (plate_size.Z + self.style.rib.depth) / 2, 0)))
                    )
                    with BuildSketch(side_plane):
                        Trapezoid(part_area_size.X, self.style.rib.depth, 30)
                    extrude(amount=self.style.rib.width)
                mirror(rib.part, Plane.XZ)  # place on both sides

        # Add/subtract parts
        result = face_plate.part
        assert result is not None
        if self.part:
            result = self.part.intersect_with(result, plate)

        return Compound(label="face_plate", children=[result])

import math
from build123d import (
    BuildSketch,
    BuildPart,
    Vector,
    Plane,
    Compound,
    RectangleRounded,
    Trapezoid,
    Location,
    Locations,
    mirror,
    extrude,
    Mode,
    Axis,
    SlotOverall,
)

from ..dimensions import RackDims, RackScrewDims, Screw1032Dims, ShelfTabDims
from .model import Model
from ..parts.model_part import ModelPart, Plate


class FacePlate(Model):
    """
    A face plate model
    """

    SHELF_TAB_HOLE_WIDTH_TECMOJO = 9.28
    """Width of the tab hole found  (use 10-24 screw hole diameter for height) """
    CORNER_ROUNDING = 3.0
    """Rounding applied to corners of a face_plate"""
    STD_RIB = Vector(2.0, 1.0)
    """Default rib size for the face plate"""
    NO_RIB = Vector(0, 0)
    """Default thickness for a face plate"""
    THICKNESS = 3.5

    def __init__(
        self,
        rack_units: float,
        thickness: float = THICKNESS,
        middle_holes: bool = True,
        half_alignment: bool = False,
        rib_size: Vector = NO_RIB,
        part: ModelPart | None = None,
    ):
        """
        Create a face plate model

        Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            thickness: Thickness of the plate
            middle_holes: draw middle screw holes
            half_alignment: start the bottom with a half unit.
            rib_size: Size of the rib. Use Vector(0, 0) for no rib.
            feature: The feature to use for the plate. Defaults to None.
        """
        self.rack_units = rack_units
        self.thickness = thickness
        self.middle_holes = middle_holes
        self.half_alignment = half_alignment
        self.rib_size = rib_size
        self.part = part

    @staticmethod
    def layout_rack_screw_holes(
        rack_units: float,
        middle_holes: bool = True,
        half_height_bottom: bool = False,
    ) -> list[float]:
        """
        Layout the faceplate

        Args:
            rack_units: Number of rack units of the plate with half units being acceptable
            middle_holes: draw middle screw holes
            bottom_is_half_height: The bottom will start on the middle hole

        Returns:
                A list of offsets
        """
        bottom_half_units = 1 if half_height_bottom else 0
        full_units = (
            math.floor(rack_units - 0.5) if half_height_bottom else math.floor(rack_units)
        )
        top_half_units = 1 if (rack_units - bottom_half_units * 0.5 - full_units > 0) else 0
        offsets: list[float] = []

        # Construct the y values for the holes from 0 to height

        # bottom half units
        if bottom_half_units:
            if middle_holes:
                offsets.extend(
                    [
                        RackScrewDims.MIDDLE - RackDims.HEIGHT_1U / 2,
                        RackScrewDims.TOP - RackDims.HEIGHT_1U / 2,
                    ]
                )
            else:
                offsets.append(RackScrewDims.TOP - RackDims.HEIGHT_1U / 2)

        # middle full units
        for u in range(full_units):
            y_slot = u * RackDims.HEIGHT_1U + bottom_half_units * RackDims.HEIGHT_1U / 2
            if middle_holes:
                offsets.extend(
                    [
                        RackScrewDims.BOTTOM + y_slot,
                        RackScrewDims.MIDDLE + y_slot,
                        RackScrewDims.TOP + y_slot,
                    ]
                )
            else:
                offsets.extend([RackScrewDims.BOTTOM + y_slot, RackScrewDims.TOP + y_slot])

        # top half units
        if top_half_units:
            y_slot = RackDims.HEIGHT_1U * full_units + bottom_half_units * RackDims.HEIGHT_1U / 2
            if middle_holes:
                offsets.extend([RackScrewDims.BOTTOM + y_slot, RackScrewDims.MIDDLE + y_slot])
            else:
                offsets.extend([RackScrewDims.BOTTOM + y_slot])

        return offsets

    def render(self) -> Compound:
        """
        Render the face plate

        Returns:
            A Shape
        """
        plate_size = Vector(
            RackDims.WIDTH_10INCH, self.rack_units * RackDims.HEIGHT_1U, self.thickness
        )
        part_area_size = Vector(
            plate_size.X - 2 * ShelfTabDims.WIDTH_TECMOJO - 2 * self.rib_size.X,
            plate_size.Y - 2 * self.rib_size.X,
            self.thickness,
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
                RectangleRounded(plate_size.X, plate_size.Y, FacePlate.CORNER_ROUNDING)

                # screw holes
                y_values = FacePlate.layout_rack_screw_holes(
                    rack_units=self.rack_units,
                    middle_holes=self.middle_holes,
                    half_height_bottom=self.half_alignment,
                )
                hole_pts = [
                    (x, y - plate_size.Y / 2)
                    for y in y_values
                    for x in [-RackScrewDims.DX / 2, RackScrewDims.DX / 2]
                ]
                with Locations(hole_pts):
                    # holes are made with slots
                    SlotOverall(
                        ShelfTabDims.HOLE_WIDTH_TECMOJO,
                        Screw1032Dims.HOLE,
                        mode=Mode.SUBTRACT,
                    )
            extrude(amount=plate_size.Z)

            # ribs
            if self.rib_size.X > 0:
                with BuildPart() as rib:
                    # orient the extrusion to point in the Y-Axis
                    side_plane = (
                        Plane(face_plate.faces().sort_by(Axis.Y)[0])
                        .rotated((180, 180, 0))
                        .moved(Location((0, (plate_size.Z + self.rib_size.Y) / 2, 0)))
                    )
                    with BuildSketch(side_plane):
                        Trapezoid(part_area_size.X, self.rib_size.Y, 30)
                    extrude(amount=self.rib_size.X)
                mirror(rib.part, Plane.XZ)  # place on both sides

        # Add/subtract parts
        result = face_plate.part
        assert result is not None
        if self.part:
            result = self.part.intersect_with(result, plate)

        return Compound(label="face_plate", children=[result])

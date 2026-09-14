import math
from build123d import Locations, SlotOverall, Sketch

from .dimensions import RackDims, RackScrewDims, ShelfTabDims, Screw1032Dims, rack_units_to_mm


def layout_rack_screw_holes(
    rack_units: float,
    middle_holes: bool = True,
    half_height_bottom: bool = False,
) -> list[float]:
    """
    Layout the screw holes for a faceplate on a rack according to the pattern established
    in the dimensions module.

    Args:
        rack_units: Number of rack units of the plate with half units being acceptable
        middle_holes: draw middle screw holes
        bottom_is_half_height: The bottom will start on the middle hole

    Returns:
            A list of offsets (y values) from the bottom of the rack. A single rack unit will have a
            top and bottom hole and if `middle_holes` is `True`, a middle hole will be returned as well.
    """
    bottom_half_units = 1 if half_height_bottom else 0
    full_units = math.floor(rack_units - 0.5) if half_height_bottom else math.floor(rack_units)
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
        y_slot = rack_units_to_mm(u + bottom_half_units * 0.5)
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
        y_slot = rack_units_to_mm(full_units + bottom_half_units * 0.5)
        if middle_holes:
            offsets.extend([RackScrewDims.BOTTOM + y_slot, RackScrewDims.MIDDLE + y_slot])
        else:
            offsets.extend([RackScrewDims.BOTTOM + y_slot])

    return offsets


def sketch_rack_holes(
    rack_units: float,
    middle_holes: bool = True,
    half_height_bottom: bool = False,
) -> Sketch:
    """
    Sketch the rack holes for the given rack units.
    """
    y_values = layout_rack_screw_holes(
        rack_units,
        middle_holes,
        half_height_bottom,
    )
    hole_pts = [
        (x, y - rack_units_to_mm(rack_units) / 2)
        for y in y_values
        for x in [-RackScrewDims.DX / 2, RackScrewDims.DX / 2]
    ]
    sketch = Sketch()  # Dim = 2
    for loc in Locations(hole_pts):
        # holes are made with slots
        sketch += loc * SlotOverall(ShelfTabDims.HOLE_WIDTH_TECMOJO, Screw1032Dims.HOLE)
    return Sketch(sketch)

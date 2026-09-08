from dataclasses import dataclass
from build123d import Vector, VectorLike, Part, Box, Pos, extrude, Sketch, Mode, Location

from .model_part import ModelPart, PartPiece, Plate
from ..selectors import Side, select_locations, select_location, Place
from ..elements import (
    RectangleElement,
    CrossElement,
    RectangleWithCornersElement,
    extrude_element,
    make_plate,
    RoundedCorner,
    HexHoles,
)


@dataclass
class PuckHolderStyle:
    """
    Represents the style of a wall holder, including cutout presence and lip dimensions.
    """

    has_cutout: bool = True
    """Does the holder have a cutout for the device?"""

    corner_rounding: float = 1.0
    """The rounding of the holder's corners."""

    corner_edges: float = 1.0
    """The extra width of the corner edges."""


class PuckHolder(ModelPart):
    """
    A device holder for a single device on a face plate.
    Devices are held by friction from side, top and bottom plates.
    """

    PLAIN = PuckHolderStyle(True)
    """A holder style with a rectangular cutout for the device."""

    def __init__(
        self,
        device_size: VectorLike = (0, 0, 0),
        device_rounding: float = 1.0,
        wall_thickness: float = 2.5,
        style: PuckHolderStyle = PLAIN,
        align: Place = Place.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        """
        Initialize a holder with the given style, device size, and optional label, align, shift, and padding.

        Args:
            device_size (Vector): The size of the device to hold. Defaults to Vector(0, 0, 0).
            device_rounding (float): The rounding of the device edges. Defaults to 1.0.
            wall_thickness (float): The thickness of the wall. Defaults to 2.5.
            style (PuckHolderStyle): The style of the holder.
            align (Vector): The alignment of the holder on the plate. Defaults to Vector(0, 0, 0).
            shift (Vector): The shift of the holder on the plate. Defaults to Vector(0, 0, 0).
            padding (float): The padding around the holder. Defaults to 0.0.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        assert wall_thickness > 0.5, "wall_thickness must be positive"
        super().__init__(align, shift, padding)
        self.device_size = Vector(device_size)
        self.device_rounding = device_rounding
        self.wall_thickness = wall_thickness
        self.style = style
        assert self.device_size.X > 0 and self.device_size.Y > 0 and self.device_size.Z > 0, (
            "device_size must be positive"
        )
        assert 2 * self.device_rounding < self.device_size.X, (
            "device_rounding must not exceed the width of the device"
        )
        assert self.device_rounding < self.device_size.Z, (
            "device_rounding must not exceed the depth of the device"
        )
        assert self.wall_thickness > 0.5, "wall_thickness must be positive"

    def layout_size(self, plate_size: Vector) -> Vector:
        return Vector(self.device_size.X, self.device_size.Y) + 2 * Vector(
            self.wall_thickness, self.wall_thickness
        )

    def render(self, plate: Plate) -> list[PartPiece]:
        # geometry
        dx, dy, dz, r = (
            self.device_size.X,
            self.device_size.Y,
            self.device_size.Z,
            self.device_rounding,
        )
        walls_depth = self.device_size.Z - r
        walls_z = r - (plate.size.Z if self.style.has_cutout else 0)
        w = self.wall_thickness
        e = self.style.corner_edges
        dc = e  # corner width

        def make_block_with_corners() -> Part:
            """
            Make the block of the holder by sketching the device block + extra for the corners.
            """
            sk = Sketch(
                RectangleElement(
                    dx + 2 * w, dy + 2 * w, RoundedCorner(self.style.corner_rounding)
                ).sketch()
                - CrossElement(dx + 2 * w, dy + 2 * w, w + e, w + e).sketch()
                + RectangleElement(dx, dy).sketch()
            )
            return Location((0, 0, walls_z)) * extrude(sk, amount=walls_depth)

        def make_walls() -> Part:
            """
            Make the walls of the holder as 4 plates with room for the corners.
            """
            top = make_plate(Vector(walls_depth, dx - 2 * dc, w), HexHoles())
            side = make_plate(Vector(walls_depth, dy - 2 * dc, w), HexHoles())
            # place around a box the size of the device
            device_box = Pos(0, 0, walls_depth / 2 + walls_z) * Box(dx, dy, walls_depth)
            side_locs = select_locations(device_box, [Side.RIGHT, Side.LEFT])
            top_locs = select_locations(device_box, [Side.TOP, Side.BOTTOM])
            return Part(
                top_locs[0] * top + side_locs[0] * side + top_locs[1] * top + side_locs[1] * side
            )

        def make_puck_cutout() -> Part:
            device_dz = dz / 2 if self.style.has_cutout else dz / 2 + plate.size.Z
            device_box = Pos(0, 0, device_dz) * Box(dx, dy, dz)
            base_loc = select_location(device_box, Side.BOTTOM, flip=True)
            base_sketch = RectangleWithCornersElement(dx, dz, r, [Place.LEFT]).sketch()
            return Part(base_loc * extrude(base_sketch, amount=dy))

        # basic holder shape
        holder = extrude_element(
            RectangleElement(dx + 2 * w, dy + 2 * w, RoundedCorner(self.style.corner_rounding)),
            walls_z,
        )
        holder += make_block_with_corners()
        holder += make_walls()

        return [
            PartPiece(plate.top_plane * holder),
            PartPiece(plate.bottom_plane * make_puck_cutout(), Mode.SUBTRACT),
        ]

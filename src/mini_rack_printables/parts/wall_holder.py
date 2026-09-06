from dataclasses import dataclass
from build123d import Vector, VectorLike, Part, Box, Pos, extrude, Mode, Sketch

from .model_part import ModelPart, PartPiece, Plate
from ..plates import make_plate, PlatePattern
from ..selectors import Side, select_locations, Place
from ..geometry import Rib
from ..elements import (
    extrude_element,
    RectangleElement,
    extrude_sketch,
    CrossElement,
    sketch_ring,
)


@dataclass
class WallHolderStyle:
    """
    Represents the style of a wall holder, including cutout presence and lip dimensions.
    """

    has_cutout: bool = True
    """Does the holder have a cutout for the device?"""
    front_lip: Rib | None = None
    """The front lip dimensions, if any."""
    back_lip: Rib | None = None
    """The back lip dimensions, if any."""


class WallHolder(ModelPart):
    """
    A device holder for a single device on a face plate.
    Devices are held by friction from side, top and bottom plates.
    """

    FRONT_LIP = WallHolderStyle(True, Rib(0.5, 1.0), None)
    """A wall holder style with a front lip to prevent the device from falling through."""
    BACK_LIP = WallHolderStyle(True, None, Rib(0.5, 1.0))
    """A wall holder style with a back lip to prevent the device from falling through. Default."""
    NO_LIP = WallHolderStyle(True, None, None)
    """A wall holder style without a lip."""
    NO_CUTOUT = WallHolderStyle(False, None, None)
    """A wall holder style without a cutout in the plate."""

    def __init__(
        self,
        device_size: VectorLike = (0, 0, 0),
        device_rounding: float = 1.0,
        wall_thickness: float = 2.5,
        style: WallHolderStyle = BACK_LIP,
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
            style (WallHolderStyle): The style of the holder. Defaults to BACK_LIP.
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

    def layout_size(self, plate_size: Vector) -> Vector:
        return Vector(self.device_size.X, self.device_size.Y) + 2 * Vector(
            self.wall_thickness, self.wall_thickness
        )

    def render(self, plate: Plate) -> list[PartPiece]:
        # geometry
        dx, dy, r = self.device_size.X, self.device_size.Y, self.device_rounding
        holder_depth = (
            self.device_size.Z
            - (plate.size.Z if self.style.has_cutout else 0)
            + (self.style.front_lip.depth if self.style.front_lip else 0)
        )
        w = self.wall_thickness
        e = 1.0  # corner edge
        dc = e + r  # corner width

        def make_corners() -> Part:
            """
            Make the corners of the holder by sketching a ring and subtracting a cross where walls will go.
            """
            sk = Sketch(
                sketch_ring(RectangleElement(dx, dy, r), w)
                - CrossElement(dx + 2 * w, dy + 2 * w, w + e + r, w + e + r).sketch()
            )
            return extrude(sk, amount=holder_depth)

        def make_walls() -> Part:
            """
            Make the walls of the holder as 4 plates with room for the corners.
            """
            top = make_plate(Vector(holder_depth, dx - 2 * dc, w), PlatePattern.HEX)
            side = make_plate(Vector(holder_depth, dy - 2 * dc, w), PlatePattern.HEX)
            # place around a box the size of the device
            device_box = Pos(0, 0, holder_depth / 2) * Box(dx, dy, holder_depth)
            side_locs = select_locations(device_box, [Side.RIGHT, Side.LEFT])
            top_locs = select_locations(device_box, [Side.TOP, Side.BOTTOM])
            return Part(
                top_locs[0] * top + side_locs[0] * side + top_locs[1] * top + side_locs[1] * side
            )

        def make_cutout() -> Part:
            """
            Make the cutout for the holder.
            """
            if self.style.front_lip:
                cutout = extrude_element(
                    RectangleElement(
                        dx - 2 * self.style.front_lip.width,
                        dy - 2 * self.style.front_lip.width,
                        r,
                    ),
                    self.style.front_lip.depth,
                )
                cutout += extrude_element(
                    RectangleElement(dx, dy, r),
                    plate.size.Z - self.style.front_lip.depth,
                    over=cutout,
                )
                return cutout
            else:
                return extrude_element(RectangleElement(dx, dy, r), plate.size.Z)

        # basic holder shape
        holder = make_corners()
        holder += make_walls()
        # add the back lip if needed
        if self.style.back_lip:
            lw = self.style.back_lip.width
            sk = sketch_ring(RectangleElement(dx, dy, r), w)
            sk += sketch_ring(RectangleElement(dx - 2 * lw, dy - 2 * lw, 0), lw)
            holder += extrude_sketch(sk, over=holder, amount=self.style.back_lip.depth)

        if self.style.has_cutout:
            return [
                PartPiece(plate.top_plane * holder),
                PartPiece(plate.bottom_plane * make_cutout(), Mode.SUBTRACT),
            ]
        else:
            return [PartPiece(plate.top_plane * holder)]

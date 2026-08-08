from enum import Enum, auto
from build123d import (
    Vector,
    VectorLike,
    Part,
    Box,
    Pos,
    Line,
    Plane,
    RadiusArc,
    extrude,
    make_face,
    mirror,
    Mode,
)

from ..geometry import RcAlignment, AlignmentVector
from .model_part import ModelPart, PartPiece, Plate
from ..plates import make_plate, PlatePattern
from ..face_selector import FaceSelector, select_locations
from ..primative_shapes import make_primative_prism, PrimativeRectangle, make_primative_tube


class HolderStyle(Enum):
    """
    Holder style without front or back lip.
    """

    FRONT_LIP = auto()
    """
    Front lip holder style.
    """
    BACK_LIP = auto()
    """
    Back lip holder style.
    """
    PUCK = auto()
    """
    Puck holder style.
    """

    def has_lip(self) -> bool:
        return self == HolderStyle.FRONT_LIP or self == HolderStyle.BACK_LIP

    def has_front_lip(self) -> bool:
        return self == HolderStyle.FRONT_LIP

    def has_back_lip(self) -> bool:
        return self == HolderStyle.BACK_LIP


class Holder(ModelPart):
    """
    A device holder for a single device. Devices are held by friction  from side, top and bottom plates.
    """

    LIP_DZ = 1.0
    LIP_WIDTH = 1.0

    def __init__(
        self,
        style: HolderStyle = HolderStyle.FRONT_LIP,
        device_size: VectorLike = (0, 0, 0),
        device_rounding: float = 1.0,
        wall_thickness: float = 2.5,
        puck_radius: float = 5.0,
        label: str = "holder",
        align: AlignmentVector = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        """
        Initialize a holder with the given style, device size, and optional label, align, shift, and padding.

        Args:
            style (HolderStyle): The style of the holder. Defaults to HolderStyle.PLAIN.
            device_size (Vector): The size of the device to hold. Defaults to Vector(0, 0, 0).
            label (str): The label to display on the holder. Defaults to an empty string.
            align (Vector): The alignment of the holder on the plate. Defaults to Vector(0, 0, 0).
            shift (Vector): The shift of the holder on the plate. Defaults to Vector(0, 0, 0).
            padding (float): The padding around the holder. Defaults to 0.0.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        assert wall_thickness > 0, "wall_thickness must be positive"
        assert puck_radius >= 0, "puck_radius must be non-negative"
        assert style != HolderStyle.PUCK, "PUCK style is not implemented"
        super().__init__(label, align, shift, padding)
        self.style = style
        self.device_size = Vector(device_size)
        self.device_rounding = device_rounding
        self.wall_thickness = wall_thickness
        self.puck_radius = puck_radius
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
            self.device_size.Z - plate.size.Z + (self.LIP_DZ if self.style.has_lip() else 0)
        )
        w = self.wall_thickness
        e = 1.0  # corner edge
        dc = e + r  # corner width

        def make_corners() -> Part:
            """
            Make the 4 corners of the holder
            """
            outline = (
                Line((r, 0), (r + e, 0))
                + Line((r + e, 0), (r + e, -w))
                + Line((r + e, -w), (r, -w))
                + RadiusArc((r, -w), (-w, r), radius=r + w)
                + Line((-w, r), (-w, r + e))
                + Line((-w, r + e), (0, r + e))
                + Line((0, r + e), (0, r))
            )
            # do not the inner corner unless the device has rounded corners
            if r > 0:
                outline += RadiusArc((r, 0), (0, r), radius=r)
            corner_face = make_face(Pos(-dx / 2, -dy / 2) * outline)
            corner = extrude(corner_face, amount=holder_depth)
            # use reflection to get the 3 other corners
            corner_y = mirror(corner, Plane.YZ)
            corner_xy = corner + corner_y
            return Part(corner_xy + mirror(corner_xy, Plane.XZ))

        def make_walls() -> Part:
            """
            Make the walls of the holder as 4 plates with room for the corners.
            """
            top = make_plate(Vector(holder_depth, dx - 2 * dc, w), PlatePattern.HEX)
            side = make_plate(Vector(holder_depth, dy - 2 * dc, w), PlatePattern.HEX)
            # place around a box the size of the device
            device_box = Pos(0, 0, holder_depth / 2) * Box(dx, dy, holder_depth)
            side_locs = select_locations(device_box, [FaceSelector.MAX_X, FaceSelector.MIN_X])
            top_locs = select_locations(device_box, [FaceSelector.MAX_Y, FaceSelector.MIN_Y])
            return Part(
                top_locs[0] * top + side_locs[0] * side + top_locs[1] * top + side_locs[1] * side
            )

        def make_cutout() -> Part:
            """
            Make the cutout for the holder.
            """
            if self.style.has_front_lip():
                cutout = make_primative_prism(
                    PrimativeRectangle(dx - 2 * self.LIP_WIDTH, dy - 2 * self.LIP_WIDTH, r),
                    self.LIP_DZ,
                )
                cutout += make_primative_prism(
                    PrimativeRectangle(dx, dy, r), plate.size.Z - self.LIP_DZ, over=cutout
                )
                return cutout
            else:
                return make_primative_prism(PrimativeRectangle(dx, dy, r), plate.size.Z)

        # basic holder shape
        holder = make_corners()
        holder += make_walls()
        # add the lip if needed
        if self.style.has_back_lip():
            lip = PrimativeRectangle(dx - 2 * self.LIP_WIDTH, dy - 2 * self.LIP_WIDTH, r)
            lip_width = self.wall_thickness + self.LIP_WIDTH
            holder += make_primative_tube(lip, lip_width, self.LIP_DZ, under=holder)

        return [
            PartPiece(self.label, (plate.top_plane * holder).solid()),
            PartPiece(
                self.label, (plate.bottom_plane * make_cutout()).solid(), mode=Mode.SUBTRACT
            ),
        ]

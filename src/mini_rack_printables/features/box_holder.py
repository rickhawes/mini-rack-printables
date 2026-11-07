"""A holder for a box on a faceplate."""

from dataclasses import dataclass
from typing import override

from ..core.assembler import Assembler
from ..core.block import ExtrudedBlock, PlateBlock, StackBlock
from ..core.feature import Feature, Rib
from ..core.figures import CutoutFigure, OutsetFigure, RectangleFigure
from ..core.geometry import Mm, Vec2, Vec3
from .basic_holder import BasicHolderStyle, build_basic_holder


class BoxHolder(Feature):
    """A holder for a box-shaped device on a faceplate.

    Box holders are used to hold many different types of box-shaped
    devices in an electronic rack. This feature is commonly used in
    a Faceplate model. Devices are held by friction from side, top
    and bottom plates.

    See Also:
        `Faceplate` - A model that frequently uses this feature.
        `PuckHolder` - A similar holder for puck shaped devices.
    """

    device_size: Vec3
    """The size of the device from the front perspective."""
    device_rounding: Mm
    """Rounding for the side edges of the device."""
    style: Style
    """Style of the holder."""

    @dataclass(frozen=True)
    class Style:
        """
        Represents the style of a wall holder, including cutout presence
        and lip dimensions.
        """

        has_cutout: bool = True
        """Does the holder have a cutout for the device?"""
        front_lip: Rib | None = None
        """The front lip dimensions, if any."""
        back_lip: Rib | None = None
        """The back lip dimensions, if any."""
        wall_thickness: float = 2.5
        """The thickness of the wall. Defaults to 2.5."""

    # Common styles
    FRONT_LIP: Style = Style(True, Rib(0.5, 1.0), None)
    """A wall holder style with a front lip to prevent the 
        device from falling through."""
    BACK_LIP: Style = Style(True, None, Rib(0.5, 1.0))
    """A wall holder style with a back lip to prevent the device from 
        falling through. Default."""
    NO_LIP: Style = Style(True, None, None)
    """A wall holder style without a lip."""
    NO_CUTOUT: Style = Style(False, None, None)
    """A wall holder style without a cutout in the plate."""

    def __init__(
        self,
        device_size: Vec3,
        device_rounding: Mm = 1.0,
        style: Style = BACK_LIP,
    ) -> None:
        """
        Initialize a holder with the device size.

        Args:
            device_size (Vector): The size of the device to hold.
            device_rounding (float): The rounding of the device edges. Defaults to 1.0.
            style (WallHolderStyle): The style of the holder. Defaults to BACK_LIP.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        self.device_size = device_size
        self.device_rounding = device_rounding
        self.style = style
        assert (
            self.device_size.x > 0 and self.device_size.y > 0 and self.device_size.z > 0
        ), "device_size must be positive"

    @override
    def desired_size(self) -> Feature.DesiredSize:
        wall = 2 * self.style.wall_thickness
        size = self.device_size.to_2d() + Vec2(wall, wall)
        return Feature.DesiredSize(size)

    @override
    def render(self, asm: Assembler) -> None:
        # geometry
        dx, dy, r = self.device_size.x, self.device_size.y, self.device_rounding
        holder_depth = (
            self.device_size.z
            - (asm.plate_depth if self.style.has_cutout else 0)
            + (self.style.front_lip.depth if self.style.front_lip is not None else 0)
        )
        w = self.style.wall_thickness
        e = 1.0  # corner edge

        def build_cutout() -> None:
            """
            Make the cutout for the holder.
            """
            cutout_sub = asm.make_cutout_sub()
            if self.style.front_lip is not None:
                stack = StackBlock(
                    [
                        PlateBlock(
                            dx - 2 * self.style.front_lip.width,
                            dy - 2 * self.style.front_lip.width,
                            self.style.front_lip.depth,
                            corners=r,
                        ),
                        PlateBlock(
                            dx, dy, asm.plate_depth - self.style.front_lip.depth, r
                        ),
                    ]
                )
                cutout_sub.place_block(stack)
            else:
                cutout_sub.place_block(PlateBlock(dx, dy, asm.plate_depth, r))

        def add_back_lip() -> None:
            assert self.style.back_lip is not None
            # start with the device and form the outer wall and the inner lip
            device = RectangleFigure(dx, dy, r)
            outer = OutsetFigure(device, w)
            inner = OutsetFigure(device, -self.style.back_lip.width)
            lip = ExtrudedBlock(CutoutFigure(outer, inner), self.style.back_lip.depth)
            asm.place_block(lip, Assembler.Place(offset=Vec3(0, 0, holder_depth)))

        # Cutout if needed
        if self.style.has_cutout:
            build_cutout()

        # Basic holder shape
        basic_style = BasicHolderStyle(
            outer_radius=r + w,
            inner_radius=r,
            wall_thickness=self.style.wall_thickness,
            corner_edge=e,
        )
        build_basic_holder(asm, Vec3(dx, dy, holder_depth), basic_style)
        # Add the back lip if needed
        if self.style.back_lip is not None:
            add_back_lip()

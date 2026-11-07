"""A holder for a puck shaped device."""

from dataclasses import dataclass
from typing import override

from ..core.assembler import Assembler
from ..core.block import ExtrudedBlock
from ..core.corners import RoundedCorners, SelectedCorners
from ..core.feature import Feature
from ..core.figures import RectangleFigure
from ..core.geometry import AxDir3, Bx, Mm, Vec2, Vec3
from .basic_holder import BasicHolderStyle, build_basic_holder


class PuckHolder(Feature):
    """A holder for a puck-shaped device on a faceplate.

    Puck holders are used to hold many different types of 
    puck-shaped devices in a electronic rack. This feature is
    commonly used in a Faceplate model. Devices are held by 
    friction from side, top and bottom plates.

    See Also:
        `Faceplate` - A model that frequently uses this feature.
        `WallHolder` - A similar holder for box shaped devices.
    """

    device_size: Vec3
    """The size of the device from the front perspective (XY plane)"""
    device_rounding: Mm
    """The rounding of the corners of the device"""
    style: Style
    """The style of the holder"""

    @dataclass
    class Style:
        """
        Represents the style of a wall holder, including cutout 
        presence and lip dimensions.
        """

        has_cutout: bool = True
        """Does the holder have a cutout for the front of the device?"""
        corner_edges: Mm = 1.0
        """The extra width of the corner edges."""
        wall_thickness: Mm = 2.5
        """The thickness of the wall. Defaults to 2.5."""

    PLAIN: Style = Style(True)
    """A holder style with a rectangular cutout for the device."""

    def __init__(
        self,
        device_size: Vec3,
        device_rounding: Mm = 1.0,
        style: Style = PLAIN,
    ) -> None:
        """Initialize a wall holder of a given device size and rounding.

        Args:
            device_size (Vec3): The size of the device to hold from 
                the front perspective. Defaults to Vector(0, 0, 0).
            device_rounding (Mm): The rounding of the device edges. 
                Defaults to 1.0.
            style (Style): The style of the holder. Defaults to PLAIN.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        self.device_size = device_size
        self.device_rounding = device_rounding
        self.style = style
        assert (
            self.device_size.x > 0 and self.device_size.y > 0 and self.device_size.z > 0
        ), "device_size must be positive"
        assert 2 * self.device_rounding < self.device_size.x, (
            "device_rounding must not exceed the width of the device"
        )
        assert self.device_rounding < self.device_size.z, (
            "device_rounding must not exceed the depth of the device"
        )

    @override
    def desired_size(self) -> Feature.DesiredSize:
        wall = 2 * self.style.wall_thickness
        size = self.device_size.to_2d() + Vec2(wall, wall)
        return Feature.DesiredSize(size)

    @override
    def render(self, asm: Assembler) -> None:
        # geometry
        dx, dy, dz = self.device_size.to_tuple()
        pd = asm.plate_depth
        r = self.device_rounding
        w = self.style.wall_thickness
        ce = self.style.corner_edges

        def add_front_block(plate_asm: Assembler, front_size: Vec3) -> None:
            """
            Make the block of the holder by sketching the device block + 
            extra for the corners.
            """
            block = ExtrudedBlock(
                RectangleFigure(front_size.x + 2 * w, front_size.y + 2 * w, w),
                front_size.z,
            )
            plate_asm.place_block(block)

        def sub_device_cutout(asm: Assembler) -> None:
            device_center = Vec3(
                0, 0, (dz / 2) - pd if self.style.has_cutout else (dz / 2)
            )
            device_cutout_bx = Bx(self.device_size, device_center).side_bx(
                AxDir3.Y_MINUS
            )
            device_cutout_asm = asm.make_sub(
                device_cutout_bx, z_dir=AxDir3.Y_PLUS, cutout_mode=True
            )
            # puck shape by selectively using rounded corners
            corners = SelectedCorners(
                RoundedCorners(r), bottom_left=True, bottom_right=True
            )
            cutout = ExtrudedBlock(RectangleFigure(dx, dz, corners), dy)
            device_cutout_asm.place_block(cutout)

        front_dz = max(r - pd if self.style.has_cutout else r, 0)
        front_size = Vec3(dx, dy, front_dz)
        add_front_block(asm, front_size)
        wall_asm = asm.make_sub(asm.bounds)
        build_basic_holder(
            wall_asm,
            Vec3(dx, dy, dz - r),
            BasicHolderStyle(outer_radius=w, corner_edge=ce, wall_thickness=w),
        )
        sub_device_cutout(asm)

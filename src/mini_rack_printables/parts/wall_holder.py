from dataclasses import dataclass
from build123d import Part, Box, Pos, extrude, Mode, Sketch
from typing import override

from .model_feature import ModelFeature, FeaturePiece, PlatePlanes
from ..selectors import Side, select_locations
from ..geometry import Rib, Vec3, Vec2, Mm
from ..elements_2d import RectangleElement
from ..corners import InsetCorners
from ..fills import HexHoles
from ..elements_3d import extrude_element, extrude_sketch, sketch_ring, make_plate


class WallHolder(ModelFeature):
    """
    A device holder for a single device on a face plate.
    Devices are held by friction from side, top and bottom plates.
    """

    device_rounding: Mm
    device_size: Vec3
    style: Style

    @dataclass
    class Style:
        """
        Represents the style of a wall holder, including cutout presence and lip dimensions.
        """

        has_cutout: bool = True
        """Does the holder have a cutout for the device?"""
        front_lip: Rib | None = None
        """The front lip dimensions, if any."""
        back_lip: Rib | None = None
        """The back lip dimensions, if any."""
        wall_thickness: float = 2.5
        """The thickness of the wall. Defaults to 2.5."""

    FRONT_LIP: Style = Style(True, Rib(0.5, 1.0), None)
    """A wall holder style with a front lip to prevent the device from falling through."""
    BACK_LIP: Style = Style(True, None, Rib(0.5, 1.0))
    """A wall holder style with a back lip to prevent the device from falling through. Default."""
    NO_LIP: Style = Style(True, None, None)
    """A wall holder style without a lip."""
    NO_CUTOUT: Style = Style(False, None, None)
    """A wall holder style without a cutout in the plate."""

    def __init__(
        self,
        device_size: Vec3 | None = None,
        device_rounding: Mm = 1.0,
        style: Style = BACK_LIP,
    ):
        """
        Initialize a holder with the given style, device size, and optional label, align, shift, and padding.

        Args:
            device_size (Vector): The size of the device to hold. Defaults to Vector(0, 0, 0).
            device_rounding (float): The rounding of the device edges. Defaults to 1.0.
            style (WallHolderStyle): The style of the holder. Defaults to BACK_LIP.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        self.device_size = device_size if device_size is not None else Vec3(0, 0, 0)
        self.device_rounding = device_rounding
        self.style = style
        assert self.device_size.x > 0 and self.device_size.y > 0 and self.device_size.z > 0, (
            "device_size must be positive"
        )

    @override
    def desired_size(self) -> ModelFeature.DesiredSize:
        wall = 2 * self.style.wall_thickness
        size = self.device_size.to_2d() + Vec2(wall, wall)
        return ModelFeature.DesiredSize(size)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[FeaturePiece]:
        # geometry
        dx, dy, r = self.device_size.x, self.device_size.y, self.device_rounding
        holder_depth = (
            self.device_size.z
            - (plate_planes.depth if self.style.has_cutout else 0)
            + (self.style.front_lip.depth if self.style.front_lip else 0)
        )
        w = self.style.wall_thickness
        e = 1.0  # corner edge
        dc = e + r  # corner width

        def make_corners() -> Part:
            """
            Make the corners of the holder by sketching a ring and subtracting a cross where walls will go.
            """
            sk = Sketch(
                sketch_ring(RectangleElement(dx, dy, r), w)
                - RectangleElement(dx + 2 * w, dy + 2 * w, InsetCorners(w + e + r)).sketch()
            )
            return extrude(sk, amount=holder_depth)

        def make_walls() -> Part:
            """
            Make the walls of the holder as 4 plates with room for the corners.
            """
            top = make_plate(Vec3(holder_depth, dx - 2 * dc, w), HexHoles())
            side = make_plate(Vec3(holder_depth, dy - 2 * dc, w), HexHoles())
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
                    plate_planes.depth - self.style.front_lip.depth,
                    over=cutout,
                )
                return cutout
            else:
                return extrude_element(RectangleElement(dx, dy, r), plate_planes.depth)

        # basic holder shape
        holder = make_corners()
        holder += make_walls()
        # add the back lip if needed
        if self.style.back_lip:
            lw = self.style.back_lip.width
            sk = sketch_ring(RectangleElement(dx, dy, r), w)
            sk += sketch_ring(RectangleElement(dx - 2 * lw, dy - 2 * lw), lw)
            holder += extrude_sketch(sk, over=holder, amount=self.style.back_lip.depth)

        if self.style.has_cutout:
            return [
                FeaturePiece(plate_planes.top_plane * holder),
                FeaturePiece(plate_planes.bottom_plane * make_cutout(), Mode.SUBTRACT),
            ]
        else:
            return [FeaturePiece(plate_planes.top_plane * holder)]

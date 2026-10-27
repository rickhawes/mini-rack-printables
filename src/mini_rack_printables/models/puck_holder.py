from dataclasses import dataclass
from typing import override

from build123d import Box, BuildSketch, Location, Mode, Part, Pos, extrude, insert

from ..core.corners import InsetCorners, RoundedCorners, SelectedCorners
from ..core.elements_2d import RectangleElement
from ..core.elements_3d import make_plate
from ..core.feature import Feature
from ..core.geometry import Bx, Mm, Vec2, Vec3
from ..core.hole_patterns import HexFill
from ..core.piece import Piece


class PuckHolder(Feature):
    """A holder for a puck-shaped device on a faceplate.

    Puck holders are used to hold many different types of puck-shaped devices in a electronic rack. This feature is
    commonly used in a Faceplate model. Devices are held by friction from side, top and bottom plates.

    See Also:
        `Faceplate` - A model that frequently uses this feature.
        `WallHolder` - A similar holder for box shaped devices.
    """

    device_size: Vec3
    """The size of the device from the front perspective."""
    device_rounding: Mm
    """The rounding of the corners of the device"""
    style: Style
    """The style of the corner"""

    @dataclass
    class Style:
        """
        Represents the style of a wall holder, including cutout presence and lip dimensions.
        """

        has_cutout: bool = True
        """Does the holder have a cutout for the device?"""
        corner_rounding: Mm = 1.0
        """The rounding of the holder's corners."""
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
            device_size (Vec3): The size of the device to hold from the front perspective. Defaults to Vector(0, 0, 0).
            device_rounding (Mm): The rounding of the device edges. Defaults to 1.0.
            style (Style): The style of the holder. Defaults to PLAIN.
        """
        assert device_rounding >= 0, "device_rounding must be non-negative"
        self.device_size = device_size
        self.device_rounding = device_rounding
        self.style = style
        assert self.device_size.x > 0 and self.device_size.y > 0 and self.device_size.z > 0, (
            "device_size must be positive"
        )
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
    def render(self, plate: Bx) -> list[Piece]:
        # geometry
        dx, dy, dz = self.device_size.to_tuple()
        r = self.device_rounding
        walls_depth = self.device_size.z - r
        walls_z = r - (plate.size.z if self.style.has_cutout else 0)
        w = self.style.wall_thickness
        e = self.style.corner_edges
        dc = e  # corner width

        def make_block_with_corners() -> Part:
            """
            Make the block of the holder by sketching the device block + extra for the corners.
            """
            with BuildSketch() as sk:
                _ = insert(
                    RectangleElement(dx + 2 * w, dy + 2 * w, self.style.corner_rounding).sketch()
                )
                _ = insert(
                    RectangleElement(dx + 2 * w, dy + 2 * w, InsetCorners(w + e)).sketch(),
                    mode=Mode.SUBTRACT,
                )
                _ = insert(RectangleElement(dx, dy).sketch())
            assert sk.sketch is not None
            # pyrefly: ignore[bad-argument-type]
            return Location((0, 0, walls_z)) * extrude(sk.sketch, amount=walls_depth)

        def make_walls() -> Part:
            """
            Make the walls of the holder as 4 plates with room for the corners.
            """
            top = make_plate(Vec3(walls_depth, dx - 2 * dc, w), HexFill())
            side = make_plate(Vec3(walls_depth, dy - 2 * dc, w), HexFill())
            # place around a box the size of the device
            device_box = Pos(0, 0, walls_depth / 2 + walls_z) * Box(dx, dy, walls_depth)
            # side_locs = select_locations(device_box, [Direction.RIGHT, Direction.LEFT])
            # top_locs = select_locations(device_box, [Direction.TOP, Direction.BOTTOM])
            # with BuildPart() as pb:
            #     _ = insert(top_locs[0] * top)
            #     _ = insert(side_locs[0] * side)
            #     _ = insert(top_locs[1] * top)
            #     _ = insert(side_locs[1] * side)
            assert pb.part is not None
            return pb.part

        def make_puck_cutout() -> Part:
            device_dz = dz / 2 if self.style.has_cutout else dz / 2 + plate_planes.depth
            device_box = Pos(0, 0, device_dz) * Box(dx, dy, dz)
            base_loc = select_location(device_box, Direction.BOTTOM, flip=True)
            # puck shape by selectively using rounded corners
            corners = SelectedCorners(RoundedCorners(r), top_left=True, bottom_left=True)
            base_sketch = RectangleElement(dx, dz, corners).sketch()
            return Part(base_loc * extrude(base_sketch, amount=dy))

        # basic holder shape
        holder = extrude_element(
            RectangleElement(dx + 2 * w, dy + 2 * w, self.style.corner_rounding),
            walls_z,
        )
        holder += make_block_with_corners()
        holder += make_walls()

        return [
            Piece(plate_planes.top_plane * holder),
            Piece(plate_planes.bottom_plane * make_puck_cutout(), cut=True),
        ]

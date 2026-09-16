from dataclasses import dataclass
from build123d import Vector, Compound, Location, mirror, Plane, Part, Sketch, extrude, Axis

from ..dimensions import ShelfTabDims, RackDims, rack_units_to_mm
from ..parts.model_part import ModelPart
from ..selectors import Side, select_plane, Place
from ..elements import (
    Element2D,
    extrude_element,
    RectangleElement,
    HexHoles,
    SquareCorners,
    TrapezoidElement,
)
from ..rack_holes import sketch_rack_holes
from .model import Model


class Shelf(Model):
    @dataclass
    class Style:
        """
        Parameters for the style of the rack shelf.
        """

        base_thickness: float = 4.0
        """Thickness of the base of the rack shelf."""
        wall_thickness: float = 3.0
        """Thickness of the wall of the rack shelf."""
        face_thickness: float = 3.0
        """Thickness of the face of the rack shelf."""
        face_rounding: float = 3.0
        """Rounding of the face of the rack shelf."""
        shelf_depth: float = RackDims.DEPTH_8INCH
        """Whether the rack shelf has a ten inch depth."""
        wall_inset: float = 20
        """Inset of the from the back of the rack shelf."""
        open_face: bool = True
        """Whether the face of the rack shelf is open or closed."""
        middle_holes: bool = True
        """Whether the rack shelf plate has middle holes."""
        half_height_bottom: bool = False
        """Whether the rack shelf plate has half-height bottom holes."""

    OPEN_FACE = Style(open_face=True)
    """A rack shelf with an open face."""

    CLOSE_FACE = Style(open_face=False)
    """A rack shelf with a closed face."""

    def __init__(
        self, rack_units: float = 1.0, style: Style = OPEN_FACE, part: ModelPart | None = None
    ):
        """
        A rack shelf with either an open or closed face.

        Args:
            rack_units: The number of rack units the shelf spans.
            style: The style of the rack shelf.
            part: The part to render on the rack shelf.
        """
        self.rack_units = rack_units
        self.style = style
        assert 4 * style.wall_inset < style.shelf_depth, (
            "wall_inset must be less than shelf_depth / 4"
        )

    def render(self) -> Compound:
        # geometry
        base_size = Vector(
            ShelfTabDims.MAX_DX_TABS,
            self.style.shelf_depth,
            self.style.base_thickness,
        )

        # wall
        def make_wall() -> Part:
            wall_size = Vector(
                base_size.Y,
                rack_units_to_mm(self.rack_units),
                self.style.wall_thickness,
            )
            inset = self.style.wall_inset
            wall_plane = (
                select_plane(base_plate, Side.MIN_X)
                .moved(
                    Location(
                        (
                            (wall_size.X - base_size.Y) / 2,
                            -wall_size.Y / 2 + base_size.Z / 2,
                            -wall_size.Z,
                        )
                    )
                )
                .rotated((180, 0, 0))
            )
            wall_sketch = Element2D.combine(
                [
                    RectangleElement(inset, 2*base_size.Z),
                    TrapezoidElement(
                        wall_size.Y,
                        wall_size.X / 2 - inset,
                        angle1=90,
                        minor_width=2*base_size.Z,
                        rotate=90,
                    ),
                    RectangleElement(
                        wall_size.X / 2,
                        wall_size.Y,
                        fill=HexHoles(),
                        corners=SquareCorners(base_size.Z),  # insets the fill area a bit
                    ),
                ],
                axis=Axis.X,
                anchor=Place.BOTTOM,
            )
            return wall_plane * extrude(wall_sketch, wall_size.Z)

        # add face
        def make_face() -> Part:
            face_size = Vector(
                RackDims.WIDTH_10INCH,
                rack_units_to_mm(self.rack_units),
                self.style.face_thickness,
            )
            face_plane = select_plane(base_plate, Side.MIN_Y).moved(
                Location((0, (face_size.Y - base_size.Z) / 2, -face_size.Z))
            )
            face_sketch = RectangleElement(
                face_size.X, face_size.Y, self.style.face_rounding
            ).sketch()
            face_sketch -= sketch_rack_holes(
                self.rack_units, self.style.middle_holes, self.style.half_height_bottom
            )
            if self.style.open_face:
                face_sketch -= RectangleElement(
                    ShelfTabDims.MAX_DX_TABS - 2 * self.style.wall_thickness, face_size.Y
                ).sketch()

            return face_plane * extrude(Sketch(face_sketch), face_size.Z)

        # shelf
        base_plate = extrude_element(RectangleElement(base_size.X, base_size.Y), base_size.Z)
        shelf = Part()
        shelf += base_plate
        wall = make_wall()
        shelf += wall
        shelf += mirror(wall, about=Plane.YZ)
        shelf += make_face()
        shelf.label = "shelf"

        return shelf

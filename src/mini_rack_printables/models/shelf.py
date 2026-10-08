from dataclasses import dataclass
from build123d import Compound, Location, mirror, Plane, Part, Sketch, extrude
from typing import override, final

from ..core.dimensions import ShelfTabDims, RackDims, rack_units_to_mm
from ..core.geometry import Bx, Vec3, Mm
from ..core.model_feature import FeatureList, PlatePlanes
from ..core.layouts import FeatureLayout, GridLayout
from ..core.selectors import Side, select_plane, Place, Ax
from ..core.elements_2d import Element2D, RectangleElement, TrapezoidElement
from ..core.elements_3d import extrude_element
from ..core.corners import SquareCorners
from ..core.fills import HexHoles
from ..core.holes import sketch_rack_holes
from ..core.model import Model


@final
class Shelf(Model):
    @dataclass(frozen=True)
    class Style:
        """
        Parameters for the style of the rack shelf.
        """

        base_thickness: Mm = 4.0
        """Thickness of the base of the rack shelf."""
        wall_thickness: Mm = 3.0
        """Thickness of the wall of the rack shelf."""
        face_thickness: Mm = 3.0
        """Thickness of the face of the rack shelf."""
        face_rounding: Mm = 3.0
        """Rounding of the face of the rack shelf."""
        shelf_depth: Mm = RackDims.DEPTH_8INCH
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
        self,
        rack_units: float = 1.0,
        style: Style = OPEN_FACE,
        shelf_features: FeatureList | None = None,
        shelf_layout: FeatureLayout | None = None,
    ):
        """
        A rack shelf with either an open or closed face.

        Args:
            rack_units: The number of rack units the shelf spans.
            style: The style of the rack shelf.
            shelf_parts: The part to render on the rack shelf.
            shelf_layout: The layout of the rack shelf.
        """
        self.rack_units = rack_units
        self.style = style
        self.shelf_features = shelf_features
        self.shelf_layout = shelf_layout if shelf_layout is not None else GridLayout()
        assert 4 * style.wall_inset < style.shelf_depth, (
            "wall_inset must be less than shelf_depth / 4"
        )

    @override
    def render(self) -> Compound:
        # geometry
        base_size = Vec3(
            ShelfTabDims.MAX_DX_TABS,
            self.style.shelf_depth,
            self.style.base_thickness,
        )
        plate_size = Vec3(
            base_size.x - 2 * self.style.wall_thickness,
            base_size.y - self.style.face_thickness,
            base_size.z,
        )

        # wall
        def make_wall(base_plate: Part) -> Part:
            wall_size = Vec3(
                base_size.y,
                rack_units_to_mm(self.rack_units),
                self.style.wall_thickness,
            )
            inset = self.style.wall_inset
            wall_plane = (
                select_plane(base_plate, Side.MIN_X)
                .moved(
                    Location(
                        (
                            (wall_size.x - base_size.y) / 2,
                            -wall_size.y / 2 + base_size.z / 2,
                            -wall_size.z,
                        )
                    )
                )
                .rotated((180, 0, 0))
            )
            wall_base = RectangleElement(inset, 2 * base_size.z)
            wall_trans = TrapezoidElement(
                wall_size.y,
                wall_size.x / 2 - inset,
                angle1=90,
                minor_width=2 * base_size.z,
                rotate=90,
            )
            wall_holes = RectangleElement(
                wall_size.x / 2,
                wall_size.y,
                fill=HexHoles(),
                corners=SquareCorners(base_size.z),  # insets the fill area a bit
            )
            wall_sketch = Element2D.combine(
                [wall_base, wall_trans, wall_holes], Ax.X, Place.BOTTOM
            )
            return wall_plane * extrude(wall_sketch, wall_size.z)

        # add face
        def make_face_plate(base_plate: Part) -> Part:
            face_size = Vec3(
                RackDims.WIDTH_10INCH,
                rack_units_to_mm(self.rack_units),
                self.style.face_thickness,
            )
            face_plane = select_plane(base_plate, Side.MIN_Y).moved(
                Location((0, (face_size.y - base_size.z) / 2, -face_size.z))
            )
            face_sketch = RectangleElement(
                face_size.x, face_size.y, self.style.face_rounding
            ).sketch()
            face_sketch -= sketch_rack_holes(
                self.rack_units, self.style.middle_holes, self.style.half_height_bottom
            )
            if self.style.open_face:
                face_sketch -= RectangleElement(
                    ShelfTabDims.MAX_DX_TABS - 2 * self.style.wall_thickness, face_size.y
                ).sketch()

            return face_plane * extrude(Sketch(face_sketch), face_size.z)

        # shelf
        def make_shelf() -> Part:
            s = Part()
            base_plate = extrude_element(RectangleElement(base_size.x, base_size.y), base_size.z)
            s += base_plate
            wall = make_wall(base_plate)
            s += wall
            s += mirror(wall, about=Plane.YZ)
            s += make_face_plate(base_plate)
            s.label = "shelf"
            return s

        shelf = make_shelf()
        if self.shelf_features:
            shelf_plate = PlatePlanes(Bx(size=plate_size, shift=Vec3(0, 0, plate_size.z / 2)))
            pieces = FeatureLayout.render_pieces(
                self.shelf_features, shelf_plate, self.shelf_layout
            )
            shelf = FeatureLayout.assemble_pieces(shelf, pieces)
        return shelf

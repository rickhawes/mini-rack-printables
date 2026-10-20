from typing import final

from build123d import Location, Part, Plane, BuildPart, insert, Mode

from .elements_3d import Element3D
from .feature import Feature, FeatureList
from .geometry import Ax3, AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .layouts import FeatureLayout
from .model import Model
from .piece import Piece
from .row_column_collection import RowColumnCollection


@final
class Modeler:
    """Helper to assemble elements and features.

    A combiner that create a 3D element

    See Also:
        `Model` and its subclasses
    """

    plane: Plane
    """The plane of the model to place elements"""
    base_bounds: Rc
    """The base bounds of the model"""
    base_depth: Mm
    """The base depth of the model"""

    pieces: list[Piece]
    """The pieces placed on this model"""
    sub_modelers: list[Modeler]
    """Modelers attached to this model"""

    def __init__(
        self,
        plane: Plane = Plane.XY,
        base_bounds: Rc | None = None,
        base_depth: Mm = 0,
    ) -> None:
        self.plane = plane
        self.base_bounds = base_bounds if base_bounds is not None else Rc(Vec2(0, 0))
        self.base_depth = base_depth
        self.pieces = []
        self.sub_modelers = []

    @classmethod
    def make_on_bx(cls, bx: Bx, side: AxDir3, z_dir: AxDir3) -> Modeler:
        """Place an element"""
        side_center = bx.side_center(side)
        side_rc = Rc(bx.side_size(side))
        side_depth = bx.side_depth(side)
        plane = Plane(
            origin=side_center.to_vector(),
            z_dir=z_dir.to_plane_z_dir(),
            x_dir=z_dir.to_plane_x_dir(),
        )
        return Modeler(plane, side_rc, side_depth)

    @classmethod
    def make_on_element(
        cls, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        if center is None:
            center = Vec3(0, 0, base.size.z / 2)
        bx = Bx(base.size, center)
        return Modeler.make_on_bx(bx, side, z_dir=side)

    @classmethod
    def make_with_element(
        cls, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        md = Modeler.make_on_element(base, center, side)
        part = Plane.XY * Location((0, 0, base.size.z / 2)) * base.render()
        md.add_pieces([Piece(part)])
        return md

    def place_center(self, element: Element3D, place: Dir2) -> Vec2:
        element_rc = Rc(element.size.to_2d())
        return self.base_bounds.place_center(element_rc, place)

    def place_element(self, element: Element3D, place: Dir2, cut: bool = False) -> None:
        center = self.place_center(element, place)
        self.add_element(element, center, cut)

    def add_element(
        self, element: Element3D, centers: Vec2 | list[Vec2] | None, cut: bool = False
    ) -> None:
        if centers is None:
            centers = [Vec2(0, 0)]
        elif isinstance(centers, Vec2):
            centers = [centers]
        assert isinstance(centers, list)
        rendered = element.render()
        pieces: list[Piece] = []
        for c in centers:
            offset = Location((0, 0, -element.size.z / 2 if cut else element.size.z / 2))
            center = Location(c.to_vector())
            pieces.append(Piece(self.plane * center * offset * rendered, cut))
        self.add_pieces(pieces)

    def add_pieces(self, pieces: list[Piece]) -> None:
        """Add a piece to the model"""
        self.pieces.extend(pieces)

    def mirror(self, axis: Ax3, times: int = 1) -> None:
        """Mirror the last piece"""

    def layout_features(self, features: list[Feature], layout: FeatureLayout) -> None:
        pass

    def add_modeler(self, child: Modeler) -> None:
        self.sub_modelers.append(child)

    def add_modeler_on_element(
        self, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        md = Modeler.make_on_element(base, center, side)
        self.add_modeler(md)
        return md

    def render_pieces(
        self,
        features: FeatureList,
        area: Rc,
        layout: FeatureLayout
    ) -> list[Piece]:
        """
        Render all `features` using the given `plate` and `layout` algorithm.
        """
        pieces: list[Piece] = []
        sub_area = layout.layout_features(features, area)
        for feature, _, _, index in RowColumnCollection(features):
            feature_plate = Vec3(sub_area[index].size.x, sub_area[index].size.y, self.base_depth)
            feature_pieces = feature.render(feature_plate)
            pieces.extend(feature_pieces)
        return pieces

    @staticmethod
    def assemble_pieces(to_part: Part, pieces: list[Piece]) -> Part:
        """
        Add `pieces` with `to_part` to create the final result.
        """
        with BuildPart() as result:
            _ = insert(to_part)
            for piece in pieces:
                _ = insert(piece.part, mode=Mode.SUBTRACT if piece.cut else Mode.ADD)
        if result.part is None:
            raise ValueError("Part was not created")
        # noinspection bad-return
        return result.part




    def render(self) -> Model.Rendering:
        pieces: list[Piece] = []
        pieces.extend(self.pieces)
        for node in self.sub_modelers:
            pieces.extend(node.pieces)
        add_parts: list[Part] = [p.part for p in pieces if not p.cut]
        sub_parts: list[Part] = [p.part for p in pieces if p.cut]
        part = Part(Part(add_parts) - Part(sub_parts))
        return Model.Rendering(part)

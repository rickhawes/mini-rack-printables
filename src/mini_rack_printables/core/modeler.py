from typing import final

from build123d import BuildPart, Location, Mode, Part, Plane, insert

from .elements_3d import Element3D
from .feature import Feature, FeatureList
from .geometry import AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .layouts import Layout
from .model import Model
from .piece import Piece


@final
class Modeler:
    """Helper to assemble elements and features.

    A combiner that create a 3D element

    See Also:
        `Model` and its subclasses
    """

    origin: Vec3
    """The origin of the model being created"""
    z_dir: AxDir3
    """The axis of the plane being created"""
    base_bounds: Rc
    """The base bounds of the model"""
    base_depth: Mm
    """The base depth of the model"""
    pieces: list[Piece]
    """The pieces placed on this model"""
    sub_modelers: list[Modeler]
    """Modelers attached to this model"""
    _plane: Plane
    """The plane of the model to place elements"""

    def __init__(
        self,
        origin: Vec3 = Vec3(0, 0, 0),
        z_dir: AxDir3 = AxDir3.Z_PLUS,
        base_bounds: Rc | None = None,
        base_depth: Mm = 0,
    ) -> None:
        self.origin = origin
        self.z_dir = z_dir
        self._plane = Plane(
            origin=origin.to_vector(), z_dir=z_dir.to_plane_z_dir(), x_dir=z_dir.to_plane_x_dir()
        )
        self.base_bounds = base_bounds if base_bounds is not None else Rc(Vec2(0, 0))
        self.base_depth = base_depth
        self.pieces = []
        self.sub_modelers = []

    @classmethod
    def make_on_bx(
        cls, bx: Bx, side: AxDir3 = AxDir3.Z_PLUS, z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        """Place an element"""
        side_center = bx.side_center(side)
        side_rc = Rc(bx.side_size(side))
        side_depth = bx.side_depth(side)
        return Modeler(origin=side_center, z_dir=z_dir, base_bounds=side_rc, base_depth=side_depth)

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

    def place_bx(self, size: Vec3, place: Dir2) -> Bx:
        element_rc = Rc(size.to_2d())
        center = self.base_bounds.place_center(element_rc, place).to_3d(
            z=size.z / 2 + self.origin.z
        )
        return Bx(size, center)

    def place_element(self, element: Element3D, place: Dir2, cut: bool = False) -> None:
        center = self.place_bx(element.size, place).center.to_2d()
        self.add_element(element, center, cut)

    def add_element(
        self, element: Element3D, centers: Vec2 | list[Vec2] | None = None, cut: bool = False
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
            pieces.append(Piece(self._plane * center * offset * rendered, cut))
        self.add_pieces(pieces)

    def add_pieces(self, pieces: list[Piece]) -> None:
        """Add a piece to the model"""
        self.pieces.extend(pieces)

    def layout_features(self, features: list[Feature], layout: Layout) -> None:
        pass

    def add_modeler(self, child: Modeler) -> None:
        self.sub_modelers.append(child)

    def add_modeler_on_element(
        self, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        md = Modeler.make_on_element(base, center, side)
        self.add_modeler(md)
        return md

    def add_modeler_on_bx(
        self, bx: Bx, side: AxDir3 = AxDir3.Z_PLUS, z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        md = Modeler.make_on_bx(bx, side, z_dir)
        self.add_modeler(md)
        return md

    def add_features(self, features: FeatureList, area: Rc, layout: Layout) -> None:
        """
        Render all `features` using the given `plate` and `layout` algorithm.
        """
        pieces: list[Piece] = []
        sections = layout.layout_features(features, area)
        for section in sections:
            z = self.origin.z - self.base_depth/2
            center = (section.origin - section.bounds.center).to_3d(z)
            size = Vec3(section.bounds.size.x, section.bounds.size.y, self.base_depth)
            feature_plate = Bx(size, center)
            feature_pieces = section.feature.render(feature_plate)
            pieces.extend(feature_pieces)
        self.add_pieces(pieces)

    def all_pieces(self) -> list[Piece]:
        """
        Return a list of all `Piece`s in the modeler including the ones in sub-modelers
        """
        pieces: list[Piece] = []
        pieces.extend(self.pieces)
        for node in self.sub_modelers:
            pieces.extend(node.all_pieces())
        return pieces

    def render(self) -> Model.Rendering:
        pieces = self.all_pieces()
        add_parts = [p.part for p in pieces if not p.cut]
        sub_parts = [p.part for p in pieces if p.cut]
        part = Part(Part(add_parts) - Part(sub_parts))
        return Model.Rendering(part)

    @staticmethod
    def _assemble_pieces(pieces: list[Piece]) -> Part:
        """
        Add `pieces` with `to_part` to create the final result.
        """
        with BuildPart() as result:
            for piece in pieces:
                _ = insert(piece.part, mode=Mode.SUBTRACT if piece.cut else Mode.ADD)
        if result.part is None:
            raise ValueError("Part was not created")
        # noinspection bad-return
        return result.part

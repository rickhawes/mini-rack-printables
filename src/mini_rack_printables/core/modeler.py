from typing import final

from build123d import Location, Part, Plane

from .elements_3d import Element3D
from .feature import Feature
from .geometry import Ax3, AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .layouts import FeatureLayout
from .model import Model
from .piece import Piece


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
    subtract: bool
    """Subtract additions from the base, otherwise add the base"""

    pieces: list[Piece]
    """The pieces placed on this model"""
    sub_modelers: list[Modeler]
    """Modelers attached to this model"""

    def __init__(
        self,
        plane: Plane = Plane.XY,
        base_bounds: Rc = Rc(Vec2(0, 0)),
        base_depth: Mm = 0,
    ) -> None:
        self.plane = plane
        self.base_bounds = base_bounds
        self.base_depth = base_depth
        self.pieces = []
        self.sub_modelers = []

    @classmethod
    def make_on_bx(cls, bx: Bx, side: AxDir3, z_dir: AxDir3) -> Modeler:
        """Place an element"""
        side_center = bx.side_center(side)
        side_rc = Rc(bx.side_size(side))
        side_depth = bx.side_depth(side)
        plane = Plane(origin=side_center.to_vector(), z_dir=z_dir.z_dir(), x_dir=z_dir.x_dir())
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
        self, element: Element3D, centers: Vec2 | list[Vec2] = Vec2(0, 0), cut: bool = False
    ) -> None:
        if isinstance(centers, Vec2):
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

    def assemble(self, features: list[Feature], layout: FeatureLayout) -> None:
        pass

    def add_modeler(self, child: Modeler) -> None:
        self.sub_modelers.append(child)

    def add_modeler_on_element(
        self, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Modeler:
        md = Modeler.make_on_element(base, center, side)
        self.add_modeler(md)
        return md

    def render(self) -> Model.Rendering:
        pieces = []
        pieces.extend(self.pieces)
        for node in self.sub_modelers:
            pieces.extend(node.pieces)
        add_parts: list[Part] = [p.part for p in pieces if not p.cut]
        sub_parts: list[Part] = [p.part for p in pieces if p.cut]
        part = Part(Part(add_parts) - Part(sub_parts))
        return Model.Rendering(part)

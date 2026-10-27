from dataclasses import dataclass
from typing import Sequence, cast, final

from build123d import Location, Part, Plane, BuildPart, insert, Mode

from .elements_3d import Element3D
from .feature import FeatureList
from .geometry import AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .layouts import Layout
from .model import Model
from .piece import Piece


@final
class Assembler:
    """Helper to assemble elements for models and features.

    TODO: explain...

    See Also:
        `Model` - Used by Model subclasses to assemble elements together
        `Feature` - Used by Feature subclasses to assemble elements together
        `Element3D` - the building blocks that are assembled together
    """

    # the base to place things on
    base: Bx
    """side of the base to place other objects"""
    side: AxDir3
    """The side of the base to place other objects"""
    cut_default: bool
    """The default for the cut parameter for pieces rendered by elements"""

    _plane: Plane
    """The plane of the model to place elements"""

    # Output
    pieces: list[Piece]
    """The pieces placed on this model"""
    sub_assemblers: list[Assembler]
    """Assemblers attached to this model"""

    # properties
    @property
    def plane_rc(self) -> Rc:
        """The base rc, relative to the assembler's plane"""
        return Rc(self.base.side_rc(self.side).size)

    @property
    def plane_depth(self) -> Mm:
        """The base depth, pelative to the assembler's plane"""
        return self.base.side_depth(self.side)

    @property
    def z_dir(self) -> AxDir3:
        """The assembler's orientation in global coordinates."""
        return self.side

    @property
    def origin(self) -> Vec3:
        """The assembler's origin in the global coordinates"""
        return self.base.side_bx(self.side).center

    def __init__(
        self,
        base: Bx,
        side: AxDir3,
        cut_default: bool = False,
    ) -> None:
        """
        Args:
            base: the base box on which everything is placed
            side: the side of the base (and the z_dir) to place everything
            cut_defaut: the default cut value for element placement
        """
        self.base = base
        self.side = side
        self.cut_default = cut_default

        # make internal structures
        self._plane = Plane(
            origin=base.side_bx(side).center.to_vector(),
            z_dir=side.to_plane_z_dir(),
            x_dir=side.to_plane_x_dir(),
        )

        # accumulations
        self.pieces = []
        self.sub_assemblers = []

    # #region Create assemblers and sub-assemblers

    @classmethod
    def make(
        cls,
        base: Bx,
        side: AxDir3 = AxDir3.Z_PLUS,
        cut_default: bool = False,
    ) -> Assembler:
        """Create a assembler.

        TODO: ...

        """
        return Assembler(base, side, cut_default)

    @classmethod
    def make_with_element(
        cls, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Create top-level assembler with the `base` element as the base"""
        if center is None:
            center = Vec3(0, 0, base.size.z / 2)
        bx = Bx(base.size, center)
        md = Assembler.make(bx, side)
        piece = Location(center.to_vector()) * base.render(cut=False)
        md.add_pieces([piece])
        return md

    def make_sub(
        self,
        base: Bx | None = None,
        side: AxDir3 | None = AxDir3.Z_PLUS,
        cut_default: bool | None = None,
    ) -> Assembler:
        """Create a sub-assembler with defaults of the current assembler."""
        if base is None:
            global_base = self.base
        else:
            global_base = base.move(self.origin)
        if side is None:
            side = self.side
        if cut_default is None:
            cut_default = self.cut_default
        assembler = Assembler(global_base, side, cut_default)
        self.sub_assemblers.append(assembler)
        return assembler

    def make_cutout_sub(self) -> Assembler:
        other_side = self.side.to_opposite()
        other_bx = self.base.side_bx(other_side).move(-self.origin)
        return self.make_sub(other_bx, cut_default=True)

    # #endregion

    @dataclass(frozen=True)
    class Place:
        """Specifies a location relative to the base plane and bounds."""

        origin: Dir2 = Dir2.CENTER
        """The region of the base where the origin is. The origin takes into account the size of the object being placed."""
        offset: Vec2 | Vec3 = Vec2(0, 0)
        """The offset of the center."""

    def place_bounds(self, size: Vec3, place: Place = Place()) -> Bx:
        """The bounding box of `size` relative the assembler's plane"""
        origin = self.plane_rc.place_center(Rc(size.x, size.y), place.origin).to_vec3()
        offset = place.offset if isinstance(place.offset, Vec3) else place.offset.to_vec3()
        center = origin + offset + Vec3(0, 0, size.z / 2)
        return Bx(size, center)

    def place_element(
        self, element: Element3D, place: Place | Sequence[Place] = Place(), cut: bool | None = None
    ) -> None:
        places = [place] if isinstance(place, Assembler.Place) else place
        pieces: list[Piece] = []
        resolved_cut = cut if cut is not None else self.cut_default
        for p in places:
            center = self.place_bounds(element.size, p).center
            piece = self._plane * Location(center.to_vector()) * element.render(resolved_cut)
            pieces.append(piece)
        self.add_pieces(pieces)

    # type CenterType = Vec2 | Sequence[Vec2] | Vec3 | Sequence[Vec3] | None

    # def stack_elements(
    #     self,
    #     elements: Sequence[Element3D],
    #     centers: CenterType = None,
    #     cut: bool | None = None,
    # ) -> None:
    #     z_offset = 0
    #     stack_dz = 0
    #     stack = Part()
    #     for element in elements:
    #         stack += (
    #             Location((0, 0, z_offset + element.size.z / 2)) * element.render(cut=False).part
    #         )
    #         stack_dz += element.size.z
    #     pieces: list[Piece] = []
    #     for c in Assembler._nomarlize_centers(centers, stack_dz):
    #         element_center = Location(c.to_vector())
    #         pieces.append(Piece(self._plane * element_center * stack, self._resolve_cut(cut)))
    #     self.add_pieces(pieces)

    # def add_element(
    #     self,
    #     element: Element3D,
    #     centers: CenterType = None,
    #     cut: bool | None = None,
    # ) -> None:
    #     """Add a `element` to model positioned by the `centers` passed in."""
    #     rendered = element.render(cut=self._resolve_cut(cut))
    #     pieces: list[Piece] = []
    #     for c in Assembler._nomarlize_centers(centers, element.size.z):
    #         element_center = Location(c.to_vector())
    #         pieces.append(self._plane * element_center * rendered)
    #     self.add_pieces(pieces)

    def add_pieces(self, pieces: list[Piece]) -> None:
        """Add pieces to the model. Do not change the pieces location"""
        self.pieces.extend(pieces)

    def add_features(self, features: FeatureList, area: Rc, layout: Layout) -> None:
        """
        Render all `features` using the given `plate` and `layout` algorithm.
        """
        pieces: list[Piece] = []
        sections = layout.layout_features(features, area)
        for section in sections:
            z = self.origin.z - self.plane_depth / 2
            center = (section.origin - section.bounds.center).to_vec3(z)
            size = Vec3(section.bounds.size.x, section.bounds.size.y, self.plane_depth)
            feature_plate = Bx(size, center)
            feature_pieces = section.feature.render(feature_plate)
            pieces.extend(feature_pieces)
        self.add_pieces(pieces)

    # def form_place(self, size: Vec3, place: Dir2) -> Bx:
    #     """Return Bx of `size` positioned on the base according to `place`."""
    #     element_rc = Rc(size.to_2d())
    #     center = self.base_bounds.place_center(element_rc, place).to_vec3(
    #         z=size.z / 2 + self.origin.z
    #     )
    #     return Bx(size, center)

    def all_pieces(self) -> list[Piece]:
        """
        Return a list of all `Piece`s in the assembler including the ones in sub-assemblers
        """
        pieces: list[Piece] = []
        pieces.extend(self.pieces)
        for node in self.sub_assemblers:
            pieces.extend(node.all_pieces())
        return pieces

    def render(self) -> Model.Rendering:
        pieces = self.all_pieces()
        add_parts = [p.part for p in pieces if not p.cut]
        sub_parts = [p.part for p in pieces if p.cut]
        with BuildPart() as assembled_part:
            for p in add_parts:
                _ = insert(p)
            for p in sub_parts:
                _ = insert(p, mode=Mode.SUBTRACT)
        assert assembled_part.part is not None
        return Model.Rendering(assembled_part.part)

    # @staticmethod
    # def _nomarlize_centers(centers: CenterType, element_depth: Mm) -> Sequence[Vec3]:
    #     if centers is None:
    #         return [Vec3(0, 0, element_depth / 2)]
    #     elif isinstance(centers, Vec2):
    #         return [Vec3(centers.x, centers.y, element_depth / 2)]
    #     elif isinstance(centers, Vec3):
    #         return [centers]
    #     elif isinstance(centers[0], Vec2):
    #         return [Vec3(v.x, v.y, element_depth / 2) for v in centers]
    #     else:
    #         return centers

    # @staticmethod
    # def _assemble_pieces(pieces: list[Piece]) -> Part:
    #     """
    #     Add `pieces` with `to_part` to create the final result.
    #     """
    #     with BuildPart() as result:
    #         for piece in pieces:
    #             _ = insert(piece.part, mode=Mode.SUBTRACT if piece.cut else Mode.ADD)
    #     if result.part is None:
    #         raise ValueError("Part was not created")
    #     # noinspection bad-return
    #     return result.part

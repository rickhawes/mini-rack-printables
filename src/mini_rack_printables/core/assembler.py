from dataclasses import dataclass
from typing import Sequence, cast, final

from build123d import BuildPart, Location, Mode, Plane, insert

from .elements_3d import Element3D
from .feature import FeatureList
from .geometry import AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .layouts import Layout, RowLayout
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
    parent: Assembler | None = None
    """If this is a sub-assembler, then the parent assembler."""
    sub_assemblers: list[Assembler]
    """Assemblers attached to this model"""
    _pieces: list[Piece] | None = None
    """If this is a top-level assembler, all the pieces"""

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
        self, base: Bx, side: AxDir3, cut_default: bool = False, parent: Assembler | None = None
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
        self._pieces = []
        self.sub_assemblers = []
        self.parent = parent

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
        return Assembler(base, side, cut_default, parent=None)

    @classmethod
    def make_with_element(
        cls, base: Element3D, center: Vec3 | None = None, side: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Create top-level assembler with the `base` element as the base.

        Args:
            base (Element3D) - the base object
            center (Vec3) - relative to the XY plane
            side (AxDir3) - the side of the base to form the assembler
        """
        if center is None:
            center = Vec3(0, 0, base.size.z / 2)
        bx = Bx(base.size, center)
        maker = Assembler.make(bx, side)
        piece = base.render(cut=False).moved(center)
        maker._append_piece(piece)
        return maker

    def make_sub(
        self,
        base: Bx | None = None,
        side: AxDir3 | None = AxDir3.Z_PLUS,
        cut_default: bool | None = None,
    ) -> Assembler:
        """Create a sub-assembler with defaults of the current assembler."""
        if base is None:
            base = self.base
        if side is None:
            side = self.side
        if cut_default is None:
            cut_default = self.cut_default
        assembler = Assembler(base, side, cut_default, parent=self)
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
        resolved_cut = cut if cut is not None else self.cut_default
        for p in places:
            center = self.place_bounds(element.size, p).center
            piece = element.render(resolved_cut)
            self.add_piece(piece, center)

    def add_features(
        self, features: FeatureList, 
        area: Rc | None = None,
        layout: Layout | None = None,
    ) -> None:
        """
        Render all `features` using the given `plate` and `layout` algorithm.
        """
        if area is None:
            area = self.base.side_rc(self.side)
        if layout is None:
            layout = RowLayout()
        sections = layout.layout_features(features, area)
        for section in sections:
            size = Vec3(section.bounds.size.x, section.bounds.size.y, self.plane_depth)
            z = -self.plane_depth / 2
            feature_plate = Bx(size, section.bounds.center.to_vec3(z))
            for p in section.feature.render(feature_plate):
                self.add_piece(p, section.origin.to_vec3(z))

    def add_piece(self, piece: Piece, position: Vec3 = Vec3(0, 0, 0)) -> None:
        """Add pieces to the model at `position` relative to the assembler's plane."""
        moved_piece = piece.moved(self._get_plane() * Location(position.to_vector()))
        self._append_piece(moved_piece)

    def _append_piece(self, piece: Piece) -> None:
        """Append `piece` to the top-level assembler's list"""
        if self.parent is None:
            assert self._pieces is not None
            self._pieces.append(piece)
        else:
            self.parent._append_piece(piece)

    def _get_plane(self) -> Plane | Location:
        if self.parent is None:
            return self._plane
        else:
            return self.parent._get_plane() * self._plane

    def all_pieces(self) -> list[Piece]:
        """All the pieces in the top and sub assemblers."""
        if self._pieces is None:
            assert self.parent is not None
            return self.parent.all_pieces()
        else:
            return self._pieces

    def make_rendering(self) -> Model.Rendering:
        with BuildPart() as builder:
            for p in self.all_pieces():
                mode = Mode.SUBTRACT if p.cut else Mode.ADD
                _ = insert(p.part, mode=mode)
        assert builder.part is not None
        return Model.Rendering(builder.part)

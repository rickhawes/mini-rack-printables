from dataclasses import dataclass
from typing import Sequence, cast, final

from build123d import BuildPart, Location, Mode, Plane, insert

from .elements_3d import Element3D
from .geometry import AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
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
    """the base plate (global coordinates)"""
    plate_side: AxDir3
    """The side of the base to place other objects"""
    cutout_mode: bool
    """The default for the cut parameter for pieces rendered by elements"""

    # the orientation of the plane
    z_dir: AxDir3
    """The direction of the Assembler's plane"""
    _plane: Plane
    """The plane of the model to place elements (global coordinates)"""

    # Output
    parent: Assembler | None = None
    """If this is a sub-assembler, then the parent assembler."""
    sub_assemblers: list[Assembler]
    """Assemblers attached to this model"""
    _pieces: list[Piece] | None = None
    """If this is a top-level assembler, all the pieces"""
    _last_element_bx: Bx | None = None
    """The the bounds of the last element that was placed. Useful for creating subs."""

    # properties
    @property
    def plate_bx(self) -> Bx:
        """The base bx (Assembler coordinates)"""
        rc = self.plate_rc
        d = self.plate_depth
        return Bx((rc.size.x, rc.size.y, d), (0, 0, d / 2 if self.cutout_mode else -d / 2))

    @property
    def plate_rc(self) -> Rc:
        """The base rc (Assembler coordinates)"""
        return Rc(self.base.side_rc(self.plate_side).size)

    @property
    def plate_depth(self) -> Mm:
        """The base depth (Assembler coordinates)"""
        return self.base.side_depth(self.plate_side)

    @property
    def origin(self) -> Vec3:
        """The assembler's origin in the global coordinates"""
        return self.base.side_bx(self.plate_side).center

    def __init__(
        self,
        plate: Bx,
        z_dir: AxDir3 = AxDir3.Z_PLUS,
        cutout_mode: bool = False,
        parent: Assembler | None = None,
    ) -> None:
        """
        Args:
            base: the base box on which everything is placed in global
            z_dir: the orientation for the placement (and the z_dir)
            cutout_mode: the default cut value for element placement and the base is above the plane
        """
        self.base = plate
        self.z_dir = z_dir
        self.plate_side = z_dir.to_opposite() if cutout_mode else z_dir
        self.cutout_mode = cutout_mode

        # make internal structures
        self._plane = Plane(
            origin=plate.side_bx(self.plate_side).center.to_vector(),
            z_dir=z_dir.to_plane_z_dir(),
            x_dir=z_dir.to_plane_x_dir(),
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
        z_dir: AxDir3 = AxDir3.Z_PLUS,
        cutout_mode: bool = False,
    ) -> Assembler:
        """Create a assembler.

        TODO: ...

        """
        return Assembler(base, z_dir, cutout_mode, parent=None)

    @classmethod
    def make_with_element(
        cls, element: Element3D, center: Vec3 | None = None, z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Create top-level assembler with the element as the plate.

        Args:
            element (Element3D) - the base object relative to the XY plane
            center (Vec3) - relative to the XY plane
            side (AxDir3) - the side of the base to form the assembler
        """
        if center is None:
            center = Vec3(0, 0, element.size.z / 2)
        bx = Bx(element.size, center)
        maker = Assembler.make(bx, z_dir)
        piece = element.render(cut=False).moved(center)
        maker._append_piece(piece)
        return maker

    def make_sub(
        self,
        plate: Bx | None = None,
        z_dir: AxDir3 | None = None,
        cutout_mode: bool | None = None,
    ) -> Assembler:
        """Create a sub-assembler with defaults of the current assembler.

        Args:
            plate (Bx) - plate in global
            side (AxDir3) - Side in realtive
            cut_default -
        """
        if plate is None:
            plate = self.base
        if z_dir is None:
            z_dir = self.z_dir
        if cutout_mode is None:
            cutout_mode = self.cutout_mode
        assembler = Assembler(plate, z_dir, cutout_mode, parent=self)
        self.sub_assemblers.append(assembler)
        return assembler

    def make_cutout_sub(self) -> Assembler:
        if self.cutout_mode:
            raise RuntimeError("Cannot make a cutout sub on a cutout sub")
        return self.make_sub(cutout_mode=True)

    def make_section_sub(self, section: Rc) -> Assembler:
        """Section relative to the plane_rc"""
        raise NotImplemented

    # #endregion

    @dataclass(frozen=True)
    class Place:
        """Specifies a location relative to the base plane and bounds."""

        origin: Dir2 = Dir2.CENTER
        """The region of the base where the origin is. The origin takes into account the size of the object being placed."""
        offset: Vec2 | Vec3 = Vec2(0, 0)
        """The offset of the center."""

    type Places = Place | Sequence[Place]

    def place_bounds(self, size: Vec3, place: Place = Place()) -> Bx:
        """The bounding box of `size` relative the assembler's plane"""
        origin = self.plate_rc.place_center(Rc(size.x, size.y), place.origin).to_vec3()
        offset = place.offset if isinstance(place.offset, Vec3) else place.offset.to_vec3()
        center = origin + offset + Vec3(0, 0, size.z / 2)
        return Bx(size, center)

    def place_element(
        self, element: Element3D, places: Places = Place(), cut: bool | None = None
    ) -> None:
        """Place a element"""
        if isinstance(places, Assembler.Place):
            places = [places]
        if len(places) == 0:
            raise ValueError("`place` must not be an empty list")
        resolved_cut = cut if cut is not None else self.cutout_mode
        for p in places:
            center = self.place_bounds(element.size, p).center
            piece = element.render(resolved_cut)
            self.add_piece(piece, center)

    def stack_element(
        self, element: Element3D, place: Place = Place(), sub_z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Place an element and create a sub-assembler on the placed."""
        center = self.place_bounds(element.size, place).center
        piece = element.render(cut=False)
        self.add_piece(piece, center)
        return self.make_sub(Bx(element.size, self.to_global(center)), z_dir=sub_z_dir)

    def add_piece(self, piece: Piece, position: Vec3 = Vec3(0, 0, 0)) -> None:
        """Add pieces to the model at `position` relative to the assembler's plane."""
        moved_piece = piece.moved(self._plane * Location(position.to_vector()))
        self._append_piece(moved_piece)

    def _append_piece(self, piece: Piece) -> None:
        """Append `piece` to the top-level assembler's list"""
        if self.parent is None:
            assert self._pieces is not None
            self._pieces.append(piece)
        else:
            self.parent._append_piece(piece)

    def to_global(self, local: Vec3) -> Vec3:
        return local + self.origin

    def to_local(self, gbl: Vec3) -> Vec3:
        return gbl - self.origin

    # def _get_plane(self) -> Plane | Location:
    #     if self.parent is None:
    #         return self._plane
    #     else:
    #         return self.parent._get_plane() * self._plane

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

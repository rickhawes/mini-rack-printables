"""Assembler places blocks into models."""

from dataclasses import dataclass
from typing import Sequence, final

import build123d as bd

from .block import Block
from .geometry import AxDir3, Bx, Dir2, Mm, Rc, Vec2, Vec3
from .piece import Piece
from .rendering import Rendering


@final
class Assembler:
    """Helper to assemble blocks for models and features.

    See Also:
        `Model` - Used by Model subclasses to assemble blocks together
        `Feature` - Used by Feature subclasses to assemble blocks together
        `Block` - the building blocks that are assembled together
    """

    @dataclass(frozen=True)
    class Plate:
        """Defines a plate for the assembler"""

        bx: Bx
        """the boundary box (global coordinates)."""
        side: AxDir3
        """The side of the plate to place other objects."""
        z_dir: AxDir3
        """The direction of the plate's plane."""
        plane: bd.Plane
        """The plane of the plate to place blocks (global coordinates)."""

        @classmethod
        def _make(cls, base: Bx, z_dir: AxDir3, cutout_mode: bool) -> Assembler.Plate:
            side = z_dir.to_opposite() if cutout_mode else z_dir
            plane = bd.Plane(
                origin=base.side_bx(side).center.to_vector(),
                z_dir=z_dir.to_plane_z_dir(),
                x_dir=z_dir.to_plane_x_dir(),
            )
            return Assembler.Plate(base, side, z_dir, plane)

    _plate: Plate
    """The plate to assemble on."""

    cutout_mode: bool
    """The default for the cut parameter for pieces rendered by blocks."""

    # Tree of assemblers for a model
    parent: Assembler | None = None
    """If this is a sub-assembler, then the parent assembler."""
    sub_assemblers: list[Assembler]

    """Assemblers attached to this model"""
    _pieces: list[Piece] | None = None
    """If this is a top-level assembler, all the pieces."""
    bounds: Bx | None = None
    """The bounds of all pieces."""

    # properties
    @property
    def plate_bx(self) -> Bx:
        """The base bx (Assembler coordinates)"""
        rc = self.plate_rc
        d = self.plate_depth
        z = d / 2 if self.cutout_mode else -d / 2
        return Bx((rc.size.x, rc.size.y, d), (0, 0, z))

    @property
    def plate_rc(self) -> Rc:
        """The base rc (Assembler coordinates)"""
        return Rc(self._plate.bx.side_rc(self._plate.side).size)

    @property
    def plate_depth(self) -> Mm:
        """The base depth (Assembler coordinates)"""
        return self._plate.bx.side_depth(self._plate.side)

    @property
    def origin(self) -> Vec3:
        """The assembler's origin in the global coordinates"""
        return self._plate.bx.side_bx(self._plate.side).center

    @property
    def z_dir(self) -> AxDir3:
        """The assembler's z_dir for placement"""
        return self._plate.z_dir

    @property
    def is_top_level(self) -> bool:
        """Is the assembler a top-level assembler"""
        return self.parent is None

    @property
    def is_sub(self) -> bool:
        """Is the assembler a sub-level assembler"""
        return self.parent is not None

    def __init__(
        self,
        _plate: Plate,
        cutout_mode: bool = False,
        parent: Assembler | None = None,
    ) -> None:
        """Create an assembler or sub-assembler.

        Args:
            plate: the base box on which everything is placed in global.
            z_dir: the orientation for the placement (and the z_dir).
            cutout_mode: the default cut value for block placement
                and the base is above the plane.
            parent: the parent assembler if any.
        """
        self._plate = _plate
        self.cutout_mode = cutout_mode
        self._pieces = []
        self.sub_assemblers = []
        self.parent = parent
        self.bounds = None

    # region Create assemblers and sub-assemblers
    #

    @classmethod
    def make(
        cls,
        base: Bx,
        z_dir: AxDir3 = AxDir3.Z_PLUS,
        cutout_mode: bool = False,
    ) -> Assembler:
        """Create a top-level assembler.

        Args:
            plate: the base box on which everything is placed in global.
            z_dir: the orientation for the placement (and the z_dir).
            cutout_mode: the default cut value for block placement and
                the base is above the plane.
        """
        plate = Assembler.Plate._make(base, z_dir, cutout_mode)
        return Assembler(plate, cutout_mode, parent=None)

    @classmethod
    def make_with_block(
        cls, block: Block, center: Vec3 | None = None, z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Create top-level assembler with the block as the plate.

        Args:
            block (Block) - the base object relative to the XY plane
            center (Vec3) - relative to the XY plane
            z_dir (AxDir3) - the side of the base to form the assembler
        """
        if center is None:
            center = Vec3(0, 0, block.size.z / 2)
        bx = Bx(block.size, center)
        asm = Assembler.make(bx, z_dir)
        piece = block.render(cut=False).moved(center)
        asm._append_piece(piece)
        return asm

    def make_sub(
        self,
        plate: Bx | None = None,
        z_dir: AxDir3 | None = None,
        cutout_mode: bool | None = None,
    ) -> Assembler:
        """Create a sub-assembler with defaults of the current assembler.

        Args:
            plate (Bx) - the plate of plate (local coordinates)
            z_dir (AxDir3) - the sub's z_dir and side of plate to use
            cutout_mode (bool) - The assembler should default to cutting
                from the plate
        """
        if plate is not None:
            # Convert the passed in plate to global
            base = plate.move(self.origin)
        else:
            base = self._plate.bx
        if z_dir is None:
            z_dir = self._plate.z_dir
        if cutout_mode is None:
            cutout_mode = self.cutout_mode
        _plate = Assembler.Plate._make(base, z_dir, cutout_mode)
        sub = Assembler(_plate, cutout_mode, parent=self)
        self.sub_assemblers.append(sub)
        return sub

    def make_cutout_sub(self) -> Assembler:
        """Make a assembler with `cutout_mode` = True on the same plate."""
        if self.cutout_mode:
            raise RuntimeError("Cannot make a cutout sub on a cutout sub")
        return self.make_sub(cutout_mode=True)

    def make_section_sub(self, section: Rc, origin: Vec2) -> Assembler:
        """Create a sub assembler on a `section` of the plate"""
        size = Vec3(section.size.x, section.size.y, self.plate_depth)
        center = Vec3(origin.x, origin.y, self.plate_bx.center.z)
        return self.make_sub(Bx(size, center))

    # #endregion

    @dataclass(frozen=True)
    class Place:
        """Specifies a location relative to the base plane and bounds."""

        origin: Dir2 = Dir2.CENTER
        """
        The region of the base where the origin is. The origin takes into 
        account the size of the object being placed.
        """
        offset: Vec2 | Vec3 = Vec2(0, 0)
        """The offset of the center."""

    type Places = Assembler.Place | Sequence[Assembler.Place]

    def place_bounds(self, size: Vec3, place: Place = Place()) -> Bx:
        """The bounding box of `size` relative the assembler's plane"""
        origin = self.plate_rc.place_center(Rc(size.x, size.y), place.origin).to_vec3()
        offset = (
            place.offset if isinstance(place.offset, Vec3) else place.offset.to_vec3()
        )
        center = origin + offset + Vec3(0, 0, size.z / 2)
        return Bx(size, center)

    def place_block(
        self, block: Block, places: Places = Place(), cut: bool | None = None
    ) -> None:
        """Place an block"""
        if isinstance(places, Assembler.Place):
            places = [places]
        if len(places) == 0:
            raise ValueError("`place` must not be an empty list")
        resolved_cut = cut if cut is not None else self.cutout_mode
        for p in places:
            center = self.place_bounds(block.size, p).center
            piece = block.render(resolved_cut)
            self.add_piece(piece, center)

    def stack_block(
        self, block: Block, place: Place = Place(), sub_z_dir: AxDir3 = AxDir3.Z_PLUS
    ) -> Assembler:
        """Place an block and create a sub-assembler on the placed."""
        center = self.place_bounds(block.size, place).center
        piece = block.render(cut=False)
        self.add_piece(piece, center)
        return self.make_sub(Bx(block.size, center), z_dir=sub_z_dir)

    def add_piece(self, piece: Piece, position: Vec3 = Vec3(0, 0, 0)) -> None:
        """Add pieces to the model at `position` relative to the assembler's plane."""
        moved_piece = piece.moved(self._plate.plane * bd.Location(position.to_vector()))
        self._append_piece(moved_piece)

    def _append_piece(self, piece: Piece) -> None:
        """Append `piece` to the top-level assembler's list"""
        # Update bounds
        if not piece.cut:
            relative = piece.bounds.move(-self.origin)
            if self.bounds is None:
                self.bounds = relative
            else:
                self.bounds = Bx.union(self.bounds, relative)
        # Place in the top-level list
        if self.parent is None:
            assert self._pieces is not None
            self._pieces.append(piece)
        else:
            # pylint: disable=protected-access
            self.parent._append_piece(piece)

    def to_global(self, local: Vec3) -> Vec3:
        """Convert a local vector to a global coordinate vector"""
        return local + self.origin

    def to_local(self, gbl: Vec3) -> Vec3:
        """Convert a global vector to a local coordinate vector"""
        return gbl - self.origin

    def all_pieces(self) -> list[Piece]:
        """All the pieces in the top and sub assemblers."""
        if self._pieces is None:
            assert self.parent is not None
            return self.parent.all_pieces()
        return self._pieces

    def make_rendering(self) -> Rendering:
        """Make a rendering for the assembler."""
        with bd.BuildPart() as builder:
            for p in self.all_pieces():
                mode = bd.Mode.SUBTRACT if p.cut else bd.Mode.ADD
                _ = bd.insert(p.part, mode=mode)
        assert builder.part is not None
        return Rendering(builder.part)

"""
3D blocks for models and features.

A core concept is the stacking of blocks to construct features and models.

See Also:
    `Figure` - for the 2d equivalent
    `Assembler` - to place blocks on top of each other
"""

import functools
import importlib.resources
import pathlib
from abc import ABC, abstractmethod
from typing import Sequence, override

import build123d as bd

from .corners import Corners
from .figures import Figure, RectangleFigure, RingFigure
from .geometry import Degree, Mm, Vec3
from .hole_patterns import HolePattern
from .piece import Piece

#
# region block interface and general Extrusion
#


class Block(ABC):
    """3d shapes that are composable by an `Assembler`"""

    @property
    @abstractmethod
    def size(self) -> Vec3:
        """Returns the size of the shape in 3d."""

    @abstractmethod
    def render(self, cut: bool = False) -> Piece:
        """Extrudes the shape centered on the plane and the z-axis of the plane"""


class ExtrudedBlock(Block):
    """A prism block is an extrusion of a 2d figure.

    Attributes:
        figure: Base 2d figure
        amount: Depth of the extrusion
        taper: The degree of taper. Default 0.

    See Also:
        Figure - For figures that can be extruded
    """

    figure: Figure
    amount: Mm
    taper: Degree

    def __init__(self, figure: Figure, amount: Mm, taper: Degree = 0) -> None:
        self.figure = figure
        self.amount = amount
        self.taper = taper

    @property
    @override
    def size(self) -> Vec3:
        size2d = self.figure.size
        return Vec3(size2d.x, size2d.y, self.amount)

    @override
    def render(self, cut: bool = False) -> Piece:
        extrusion = bd.extrude(self.figure.sketch(), self.amount, taper=self.taper)
        part = bd.Location((0, 0, -self.amount / 2)) * extrusion
        return Piece(part, cut)


# endregion
#
# region Specific block classes
#


class BoxBlock(ExtrudedBlock):
    """A basic box block with no rounding.

    See Also:
        `PlateBlock` - If rounding is needed
    """

    def __init__(self, dx: Mm, dy: Mm, dz: Mm) -> None:
        super().__init__(RectangleFigure(dx, dy), dz)


class ConeBlock(Block):
    """A cone block with a circular top and base.

    See Also:
        `CylinderBlock` - for zero taper cones.
    """

    base_radius: Mm
    top_radius: Mm
    height: Mm

    def __init__(self, base_radius: Mm, top_radius: Mm, height: Mm) -> None:
        self.base_radius = base_radius
        self.top_radius = top_radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        max_radius = max(self.base_radius, self.top_radius)
        return Vec3(2 * max_radius, 2 * max_radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        part = bd.Location((0, 0, self.height / 2)) * bd.Cone(
            self.base_radius, self.top_radius, self.height
        )
        return Piece(part, cut)


class CylinderBlock(Block):
    """A cylinder block.

    See Also:
        `ConeBlock` - for tapered cyclinder
    """

    radius: Mm
    height: Mm

    def __init__(self, radius: Mm, height: Mm) -> None:
        self.radius = radius
        self.height = height

    @property
    @override
    def size(self) -> Vec3:
        return Vec3(2 * self.radius, 2 * self.radius, self.height)

    @override
    def render(self, cut: bool = False) -> Piece:
        return Piece(bd.Cylinder(self.radius, self.height), cut)


class PlateBlock(ExtrudedBlock):
    """A extruded Rectangle figure

    See Also:
        BoxBlock - If rounding, holes and corners is not needed
    """

    def __init__(
        self,
        width: Mm,
        height: Mm,
        depth: Mm,
        corners: Mm | Corners | None = None,
        holes: HolePattern | None = None,
    ) -> None:
        super().__init__(RectangleFigure(width, height, corners, holes), depth)


class ImportBlock(Block):
    """An block formed from a BREP file or an STL file.

    BREP files are imported rapidly, while STL files are converted to a
    BREP model using the `Mesher` library which may take some time.
    STL files can be converted to a BREP model using the `import_stl.py` script.
    """

    BREP_SUFFIX: str = ".brep"
    STL_SUFFIX: str = ".stl"

    file: pathlib.Path | None = None
    asset: str | None = None
    asset_folder: str | None = None

    def __init__(
        self,
        file: pathlib.Path | None = None,
        asset: pathlib.Path | None = None,
    ) -> None:
        """
        Initialize the ImportBlock with the given path or asset
        name and optional parameters.

        Args:
            file (Path): The path to the BREP or STL file.
            asset (Path): The path to the asset to import.
        """
        if file is not None:
            if not file.exists():
                raise ValueError(f"Path does not exist: {file}")
            if not (file.suffix in [self.BREP_SUFFIX, self.STL_SUFFIX]):
                raise ValueError(f"Expected BREP or STL file, got {file.suffix}")
            self.file = file
        elif asset is not None:
            self.asset_folder = str(asset.parent)
            self.asset = asset.name
            if len(self.asset_folder) == 0:
                raise ValueError("asset must contain a folder")
        else:
            raise ValueError("Either path or asset must be provided")

    @functools.cached_property
    def shape(self) -> bd.Shape[bd.TopoDS_Solid]:
        """
        Returns the shape of the part. Cached to avoid re-importing.
        """

        def convert_stl(path: pathlib.Path) -> bd.Shape[bd.TopoDS_Solid]:
            # Import the STL file and center it around the bounding box
            importer = bd.Mesher(unit=bd.Unit.MM)
            full_mesh = importer.read(path)[0]
            center = bd.Shape.combined_center(
                [full_mesh], center_of=bd.CenterOf.BOUNDING_BOX
            )
            centered_mesh = full_mesh.move(
                bd.Location((-center.X, -center.Y, -center.Z))
            )
            return centered_mesh

        def import_path(path: bd.Path) -> bd.Shape[bd.TopoDS_Solid]:
            match path.suffix:
                case self.STL_SUFFIX:
                    return convert_stl(path)
                case self.BREP_SUFFIX:
                    return bd.import_brep(path)
                case _:
                    raise ValueError(f"Unexpected file suffix: {path.suffix}")

        if self.asset_folder is not None and self.asset is not None:
            # assets may be zipped when stored, so extract to a temporary directory
            resource_path = importlib.resources.files(self.asset_folder) / self.asset
            with importlib.resources.as_file(resource_path) as asset_path:
                return import_path(asset_path)
        elif self.file is not None:
            return import_path(self.file)
        else:
            raise ValueError("No asset or path specified")

    @functools.cached_property
    def size(self) -> Vec3:
        """
        Returns the size of the import. Cached to avoid recomputing.
        """
        bbox = self.shape.bounding_box()
        assert bbox.center() == bd.Vector(0, 0, 0), (
            f"Imported part is not centered: {bbox.center()}"
        )
        return Vec3(bbox.size.X, bbox.size.Y, bbox.size.Z)

    @override
    def render(self, cut: bool = False) -> Piece:
        return Piece(self.shape.solid(), cut)


class StackBlock(Block):
    """TODO: Make dir and align work features for this stack"""

    blocks: Sequence[Block]

    def __init__(self, blocks: Sequence[Block]) -> None:
        self.blocks = blocks

    @property
    @override
    def size(self) -> Vec3:
        return Vec3(
            max(e.size.x for e in self.blocks),
            max(e.size.y for e in self.blocks),
            sum(e.size.z for e in self.blocks),
        )

    def render(self, cut: bool = False) -> Piece:
        size = self.size
        stack_dz = -size.z / 2
        stack = bd.Part()
        for blk in self.blocks:
            loc = bd.Location((0, 0, stack_dz + blk.size.z / 2))
            stack += loc * blk.render(cut=False).part
            stack_dz += blk.size.z
        return Piece(stack, cut=cut)


class TubeBlock(ExtrudedBlock):
    """Using the `base` figure create extruded ring block.

    Attributes:
        base (Figure) - base figure for the tubes inner shape
        thickness (Mm) - thickness of the tube's walls
        depth (Mm) - the z-dimension of the tube.
    """

    def __init__(self, base: Figure, thickness: Mm, depth: Mm) -> None:
        super().__init__(RingFigure(base, thickness), depth)


# endregion

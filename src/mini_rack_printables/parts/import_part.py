from pathlib import Path
from typing import override
from importlib.resources import as_file, files
from functools import cached_property
from build123d import (
    Vector,
    import_brep,
    Box,
    Mode,
    Location,
    Mesher,
    CenterOf,
    Unit,
)
from build123d.topology import Shape, Solid


from .model_part import ModelPart, PartPiece, PlatePlanes
from ..dimensions import E
from ..geometry import Vec3


class ImportPart(ModelPart):
    """
    Make a part from a BREP file or a STL file.
    BREP files are imported rapidly, while STL files are converted to a BREP model using the `Mesher` library which may take some time.
    STL files can be converted to a BREP model using the `import_stl.py` script.
    Imported shapes should have a rectangular outline, if `cutout` is True.
    """

    BREP_SUFFIX: str = ".brep"
    STL_SUFFIX: str = ".stl"
    ASSET_PATH: str = "mini_rack_printables.assets"

    path: Path | None = None
    asset: str | None = None
    cutout: bool = True

    def __init__(
        self,
        path: Path | None = None,
        asset: str | None = None,
        cutout: bool = True,
    ):
        """
        Initialize the ImportPart with the given path or asset name and optional parameters.

        Args:
            path (Path): The path to the BREP or STL file.
            asset (str): The name of the asset to import.
            cutout (bool, optional): Whether to cut out the part from the enclosing model or place on top of it. Defaults to True.
        """
        if path:
            if not path.exists():
                raise ValueError(f"Path does not exist: {path}")
            if not (path.suffix == self.BREP_SUFFIX or path.suffix == self.STL_SUFFIX):
                raise ValueError(f"Expected BREP or STL file, got {path.suffix}")
        elif asset is None:
            raise ValueError("Either path or asset must be provided")
        self.path = path
        self.asset = asset
        self.cutout = cutout

    @cached_property
    def shape(self) -> Shape[Solid]:
        """
        Returns the shape of the part. Cached to avoid recomputing.
        """

        def convert_stl(path: Path) -> Shape[Solid]:
            # Import the STL file and center it around the bounding box
            importer = Mesher(unit=Unit.MM)
            full_mesh = importer.read(path)[0]
            center = Shape.combined_center([full_mesh], center_of=CenterOf.BOUNDING_BOX)
            centered_mesh = full_mesh.move(Location((-center.X, -center.Y, -center.Z)))
            return centered_mesh  # pyright: ignore[reportUnknownVariableType]

        def import_path(path: Path) -> Shape[Solid]:
            match path.suffix:
                case self.STL_SUFFIX:
                    return convert_stl(path)
                case self.BREP_SUFFIX:
                    return import_brep(path)  # pyright: ignore[reportUnknownVariableType]
                case _:
                    raise ValueError(f"Unexpected file suffix: {path.suffix}")

        if self.asset is not None:
            # assets may be zipped when stored, so extract to a temporary directory
            with as_file(files(self.ASSET_PATH) / self.asset) as asset_path:
                return import_path(asset_path)
        elif self.path is not None:
            return import_path(self.path)
        else:
            raise ValueError("No asset or path specified")

    @cached_property
    def size(self) -> Vec3:
        """
        Returns the size of the part. Cached to avoid recomputing.
        """
        bbox = self.shape.bounding_box()
        assert bbox.center() == Vector(0, 0, 0), f"Imported part is not centered: {bbox.center()}"
        return Vec3(bbox.size.X, bbox.size.Y, bbox.size.Z)

    @override
    def desired_size(self) -> ModelPart.DesiredSize:
        return ModelPart.DesiredSize(self.size.to_2d(), False)

    @override
    def render(self, plate_planes: PlatePlanes) -> list[PartPiece]:
        if self.cutout:
            # Cutout: Cutout the bottom plane and place the imported part in the cutout
            return [
                PartPiece(
                    part=plate_planes.bottom_plane
                    * Location((0, 0, plate_planes.depth / 2))
                    * Box(self.size.x - E, self.size.y - E, plate_planes.depth + E).solid(),
                    mode=Mode.SUBTRACT,
                ),
                PartPiece(
                    part=plate_planes.bottom_plane
                    * Location((0, 0, self.size.z / 2))
                    * self.shape.solid(),
                    mode=Mode.ADD,
                ),
            ]
        else:
            # No cutout, render directly on the top plane
            return [
                PartPiece(
                    part=plate_planes.top_plane
                    * Location((0, 0, self.size.z / 2))
                    * self.shape.solid(),
                    mode=Mode.ADD,
                ),
            ]

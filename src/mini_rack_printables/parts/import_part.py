from pathlib import Path
from importlib.resources import as_file, files
from functools import cached_property
from build123d import (
    Vector,
    import_brep,
    Box,
    Mode,
    Location,
    Shape,
    Mesher,
    CenterOf,
    Unit,
)

from .model_part import ModelPart, PartPiece, Plate
from ..dimensions import E


class ImportPart(ModelPart):
    """
    Make a part from a BREP file or a STL file.
    BREP files are imported rapidly, while STL files are converted to a BREP model using the `Mesher` library which may take some time.
    STL files can be converted to a BREP model using the `import_stl.py` script.
    Imported shapes should have a rectangular outline, if `cutout` is True.
    """

    BREP_SUFFIX = ".brep"
    STL_SUFFIX = ".stl"
    ASSET_PATH = "mini_rack_printables.assets"

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
    def shape(self) -> Shape:
        """
        Returns the shape of the part. Cached to avoid recomputing.
        """

        def convert_stl(path: Path) -> Shape:
            # Import the STL file and center it around the bounding box
            importer = Mesher(unit=Unit.MM)
            full_mesh = importer.read(path)[0]
            center = Shape.combined_center([full_mesh], center_of=CenterOf.BOUNDING_BOX)
            centered_mesh = full_mesh.move(Location((-center.X, -center.Y, -center.Z)))
            return centered_mesh

        def import_path(path: Path) -> Shape:
            match path.suffix:
                case self.STL_SUFFIX:
                    return convert_stl(path)
                case self.BREP_SUFFIX:
                    return import_brep(path)
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
    def size(self) -> Vector:
        """
        Returns the size of the part. Cached to avoid recomputing.
        """
        bbox = self.shape.bounding_box()
        assert bbox.center() == Vector(0, 0, 0), f"Imported part is not centered: {bbox.center()}"
        return bbox.size

    def layout_size(self) -> ModelPart.DesiredSize:
        return ModelPart.DesiredSize(self.size)

    def render(self, plate: Plate) -> list[PartPiece]:
        if self.cutout:
            # Cutout: Cutout the bottom plane and place the imported part in the cutout
            return [
                PartPiece(
                    part=plate.bottom_plane
                    * Location((0, 0, plate.size.Z / 2))
                    * Box(self.size.X - E, self.size.Y - E, plate.size.Z + E).solid(),
                    mode=Mode.SUBTRACT,
                ),
                PartPiece(
                    part=plate.bottom_plane
                    * Location((0, 0, self.size.Z / 2))
                    * self.shape.solid(),
                    mode=Mode.ADD,
                ),
            ]
        else:
            # No cutout, render directly on the top plane
            return [
                PartPiece(
                    part=plate.top_plane * Location((0, 0, self.size.Z / 2)) * self.shape.solid(),
                    mode=Mode.ADD,
                ),
            ]

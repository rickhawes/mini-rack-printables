from pathlib import Path
from .model_part import ModelPart, PartPiece, Plate
from ..geometry import RcAlignment

from build123d import Vector, import_brep, Box, Mode, Location

E = 0.05
"Small tolerance to make the imported part join with its cutout"


class ImportPart(ModelPart):
    """
    Make a part from an BREP or STEP file.

    STL files are converted to a BREP model using the `Mesher` library.
    """

    def __init__(
        self,
        path: Path,
        size: Vector,
        cutout: bool = True,
        label: str = "import",
        align: RcAlignment = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        super().__init__(label, align, shift, padding)
        self.path = path
        self.size = size
        self.cutout = cutout
        self.shape = import_brep(self.path)

    def layout_size(self, plate_size: Vector) -> Vector:
        return self.size

    def render(self, plate: Plate) -> list[PartPiece]:
        if self.cutout:
            # Cutout: Cutout the bottom plane and place the imported part in the cutout
            return [
                PartPiece(
                    name=self.label,
                    part=plate.bottom_plane
                    * Location((0, 0, plate.size.Z / 2))
                    * Box(self.size.X - E, self.size.Y - E, plate.size.Z + E).solid(),
                    mode=Mode.SUBTRACT,
                ),
                PartPiece(
                    name=self.label,
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
                    name=self.label,
                    part=plate.top_plane * Location((0, 0, self.size.Z / 2)) * self.shape.solid(),
                    mode=Mode.ADD,
                ),
            ]

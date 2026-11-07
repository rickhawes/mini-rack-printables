"""Import from a file the shape and place on it on a plate."""
from pathlib import Path
from typing import override

from ..core.assembler import Assembler
from ..core.block import BoxBlock, ImportBlock
from ..core.feature import Feature


class ImportFeature(Feature):
    """A Feature formed using a STL or BREP file"""

    ASSET_PATH: str = "mini_rack_printables.assets"

    cutout: bool = True
    block: ImportBlock

    def __init__(
        self,
        file: str | None = None,
        asset: str | None = None,
        cutout: bool = True,
    ) -> None:
        """
        Initialize the ImportPart with the given path or asset name and 
        optional parameters.

        Args:
            file (Path): The path to the BREP or STL file.
            asset (str): The name of the asset to import.
            cutout (bool, optional): Whether to cut out the part 
                from the enclosing model or place on top of it. Defaults to True.
        """
        self.cutout = cutout
        if file is not None:
            self.block = ImportBlock(file=Path(file))
        elif asset is not None:
            self.block = ImportBlock(asset=Path(ImportFeature.ASSET_PATH + "/" + asset))
        else:
            raise ValueError("Either path or asset must be provided")

    @override
    def desired_size(self) -> Feature.DesiredSize:
        return Feature.DesiredSize(self.block.size.to_2d(), False)

    @override
    def render(self, asm: Assembler) -> None:
        if self.cutout:
            # Cutout the plate first
            cutout_asm = asm.make_cutout_sub()
            box = BoxBlock(
                dx=self.block.size.x, dy=self.block.size.y, dz=asm.plate_depth
            )
            cutout_asm.place_block(box)
            # Add the import block in the cutout (explicitly override the cut mode)
            cutout_asm.place_block(self.block, cut=False)
        else:
            # Add the imported block on the plate
            asm.place_block(self.block)

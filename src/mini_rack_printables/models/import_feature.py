from functools import cached_property
from importlib.resources import as_file, files
from pathlib import Path
from typing import override

from ..core.elements_3d import BoxElement, ImportElement
from ..core.feature import Feature
from ..core.geometry import Bx
from ..core.piece import Piece
from ..core.assembler import Assembler


class ImportFeature(Feature):
    """ A Feature formed using a STL or BREP file
    """
    ASSET_PATH: str = "mini_rack_printables.assets"
    
    cutout: bool = True
    element: ImportElement

    def __init__(
        self,
        file: str | None = None,
        asset: str | None = None,
        cutout: bool = True,
    ) -> None:
        """
        Initialize the ImportPart with the given path or asset name and optional parameters.

        Args:
            file (Path): The path to the BREP or STL file.
            asset (str): The name of the asset to import.
            cutout (bool, optional): Whether to cut out the part from the enclosing model or place on top of it. Defaults to True.
        """
        self.cutout = cutout
        if file is not None:
            self.element = ImportElement(file=Path(file))
        elif asset is not None:
            self.element = ImportElement(asset=Path(ImportFeature.ASSET_PATH + "/" + asset))
        else:
            raise ValueError("Either path or asset must be provided")

    @override
    def desired_size(self) -> Feature.DesiredSize:
        return Feature.DesiredSize(self.element.size.to_2d(), False)

    @override
    def render(self, plate: Bx) -> list[Piece]:
        maker = Assembler.make(plate)

        if self.cutout:
            cutout_maker = maker.make_cutout_sub()
            # Cutout the plate first
            box = BoxElement(dx=self.element.size.x, dy=self.element.size.y, dz=plate.size.z)
            cutout_maker.place_element(box)
            # Add the import element in the cutout
            cutout_maker.place_element(self.element)
        else:
            # Add the iport element on the plate
            maker.place_element(self.element)

        return maker.all_pieces()


"""A plate cutout feature. """

from typing import override

from ..core.assembler import Assembler
from ..core.block import ExtrudedBlock, TubeBlock
from ..core.feature import Feature, Rib
from ..core.figures import Figure
from ..core.geometry import Vec2


class Cutout(Feature):
    """
    A cutout of a plate. It can also be outlined with a rib.
    """

    shape: Figure
    rib: Rib | None

    def __init__(self, shape: Figure, rib: Rib | None = None) -> None:
        """
        Args:
            shape (Figure): The 2D shape to cut out.
            rib (Rib | None): The rib to outline the cutout with.
        """
        self.shape = shape
        self.rib = rib

    @override
    def desired_size(self) -> Feature.DesiredSize:
        rib = 2 * self.rib.width if self.rib is not None else 0
        size = self.shape.size + Vec2(rib, rib)
        return Feature.DesiredSize(size, False)

    @override
    def render(self, asm: Assembler) -> None:
        # the same rendering formula is used for all types of cutouts
        cutout_asm = asm.make_cutout_sub()
        cutout_asm.place_block(ExtrudedBlock(self.shape, asm.plate_depth))

        if self.rib is not None:
            rib = TubeBlock(self.shape, self.rib.width, self.rib.depth)
            asm.place_block(rib)

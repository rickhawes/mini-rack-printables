from .import_part import ImportPart
from ..geometry import RcAlignment
from build123d import Vector


class Keystone(ImportPart):
    """
    A keystone cutout part.
    """

    def __init__(
        self,
        label: str = "keystone",
        align: RcAlignment = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        super().__init__(
            asset="keystone.brep",
            cutout=True,
            label=label,
            align=align,
            shift=shift,
            padding=padding,
        )

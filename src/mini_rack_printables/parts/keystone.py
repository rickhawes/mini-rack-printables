from .import_part import ImportPart
from ..selectors import Place
from build123d import Vector


class Keystone(ImportPart):
    """
    A keystone cutout part.
    """

    def __init__(
        self,
        align: Place = Place.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        super().__init__(
            asset="keystone.brep",
            cutout=True,
            align=align,
            shift=shift,
            padding=padding,
        )

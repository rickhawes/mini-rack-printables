from .import_part import ImportPart
from ..selector import Selector
from build123d import Vector


class JetKVM(ImportPart):
    """
    A cutout part for a holding a Jet KVM.
    """

    def __init__(
        self,
        align: Selector = Selector.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0.0,
    ):
        super().__init__(
            asset="jetkvm_trimmed.brep",
            cutout=True,
            align=align,
            shift=shift,
            padding=padding,
        )

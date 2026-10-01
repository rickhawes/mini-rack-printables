from build123d import Color, Compound, Mode

from ..parts.model_part import ModelPart, PlatePlanes
from .model import Model
from ..geometry import Bx, Vec3


class XRayModel(Model):
    """
    A X-ray model will show the nodes from a ModelPart without the plate.
    This model is useful for visualizing and debugging the structure of a ModelPart.
    """

    def __init__(self, part: ModelPart, size=Vec3(100, 100, 3.5), only_adds=True):
        self.part = part
        self.size = size
        self.only_adds = only_adds

    def render(self) -> Compound:
        plate = PlatePlanes(Bx(size=self.size, shift=Vec3(0, 0, self.size.z / 2)))

        pieces = self.part.render(plate)
        children = []
        for piece in pieces:
            if piece.mode == Mode.ADD:
                piece.part.color = Color("blue")
                piece.part.label = "add"
                children.append(piece.part)
            elif piece.mode == Mode.SUBTRACT:
                if not self.only_adds:
                    piece.part.color = Color("red")
                    piece.part.label = "subtract"
                    children.append(piece.part)
            else:
                assert False, "unhandled rendering mode"
        return Compound(label="xray", children=children)

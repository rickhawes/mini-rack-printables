from build123d import (
    Color,
    Compound,
    Location,
    Mode,
    Plane,
    Vector,
)

from ..parts.model_part import ModelPart, Plate
from .model import Model


class XRayModel(Model):
    """
    A X-ray model will show the nodes from a ModelPart without the plate.
    This model is useful for visualizing and debugging the structure of a ModelPart.
    """

    def __init__(self, part: ModelPart, size=Vector(100, 100, 3.5), only_adds=True):
        self.part = part
        self.size = size
        self.only_adds = only_adds

    def render(self) -> Compound:
        bottom_plane = Plane.XY
        top_plane = Plane.XY.moved(Location((0, 0, self.size.Z)))
        plate = Plate(self.size, top_plane, bottom_plane)

        pieces = self.part.render(plate)
        children = []
        for piece in pieces:
            if piece.mode == Mode.ADD:
                piece.part.color = Color("blue")
                piece.part.label = "add"
                children.append(piece.part)
            elif piece.mode == Mode.SUBTRACT and not self.only_adds:
                piece.part.color = Color("red")
                piece.part.label = "subtract"
                children.append(piece.part)
            else:
                assert False, "unhandled rendering mode"
        return Compound(label="xray", children=children)

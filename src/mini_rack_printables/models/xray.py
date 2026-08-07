from build123d import (
    Vector,
    Plane,
    Compound,
    Mode,
    Color,
    Location,
)

from .model import Model
from ..parts.model_part import ModelPart, Plate


class XRayModel(Model):
    """
    A X-ray model will show the nodes from a ModelPart without the plate.
    This model is useful for visualizing the structure of a ModelPart.
    """

    def __init__(self, part: ModelPart, size=Vector(100, 100, 5), only_adds=True):
        self.part = part
        self.size = size
        self.only_adds = only_adds

    def render(self) -> Compound:
        bottom_plane = Plane.XY
        top_plane = Plane.XY.moved(Location((0, 0, self.size.Z)))
        plate = Plate(self.size, top_plane, bottom_plane)

        part_nodes = self.part.render(plate)
        children = []
        for node in part_nodes:
            if node.mode == Mode.ADD:
                node.part.color = Color("blue")
                children.append(node.part)
            elif node.mode == Mode.SUBTRACT and not self.only_adds:
                node.part.color = Color("red")
                children.append(node.part)
            else:
                assert node.mode == Mode.SUBTRACT, "unhandled rendering mode"
        return Compound(label="xray", children=children)

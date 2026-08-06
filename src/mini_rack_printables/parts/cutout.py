from ..geometry import RcAlignment
from .model_part import ModelPart, PartTreeNode
from build123d import Vector, extrude, offset, Circle, BuildSketch, Mode, add


class Cutout(ModelPart):
    radius: float
    rib_size: Vector

    def __init__(
        self,
        radius: float,
        rib_size: Vector = Vector(0, 0),
        label: str = "Cutout",
        align: Vector = RcAlignment.CENTER,
        shift: Vector = Vector(0, 0),
        padding: float = 0,
    ):
        super().__init__(label, align, shift, padding)
        self.radius = radius
        self.rib_size = rib_size

    def layout_size(self, plate_size: Vector) -> Vector:
        return Vector((self.radius + self.rib_size.X) * 2, (self.radius + self.rib_size.X) * 2)

    def render(self, plate_size: Vector) -> list[PartTreeNode]:
        cir = Circle(self.radius)
        cylinder = extrude(cir, amount=plate_size.Z)
        cylinder.label = self.label
        result = [PartTreeNode(self.label, cylinder.solid(), mode=Mode.SUBTRACT)]

        if self.rib_size.X > 0:
            with BuildSketch() as sk:
                add(offset(cir, amount=self.rib_size.X), mode=Mode.ADD)
                add(cir, mode=Mode.SUBTRACT)
            rib = extrude(sk.sketch, amount=self.rib_size.Y)
            rib.label = self.label
            result += [PartTreeNode(self.label, rib.solid())]

        return result

from mini_rack_printables import Model, Modeler, BoxElement, Vec3, Vec2, SlotElement, PrismElement
from mini_rack_printables.core.elements_3d import CylinderElement


class PlateWithHoles(Model):
    size = Vec3(100, 100, 5)

    def render(self) -> Model.Rendering:
        base = BoxElement(self.size.x, self.size.y, self.size.z)
        hole = PrismElement(SlotElement(10, 5), self.size.z)
        stand = CylinderElement(5, 10)

        # Modeler is used to assemble this model
        md = Modeler.make_with_element(base)  # made with top side as the plane
        md.add_element(stand, self.stand_centers())

        # place the holes on the base using the cut mode
        md.add_element(hole, self.hole_centers(), cut=True)

        return md.render()

    def hole_centers(self) -> list[Vec2]:
        dx = self.size.x / 2 - 10
        dy = self.size.y / 2 - 10
        return [Vec2(x, y) for x in [dx, -dx] for y in [dy, 0, -dy]]

    def stand_centers(self) -> list[Vec2]:
        return [Vec2(x, y) for x in [-10, 10] for y in [0]]


rendering = PlateWithHoles().render()
rendering.show()

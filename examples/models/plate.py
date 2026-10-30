from mini_rack_printables import (
    Assembler,
    BoxElement,
    CylinderElement,
    Model,
    PrismElement,
    SlotElement,
    Vec2,
    Vec3,
)


class PlateWithHoles(Model):
    size = Vec3(100, 100, 5)

    def render(self) -> Model.Rendering:
        base = BoxElement(self.size.x, self.size.y, self.size.z)
        hole = PrismElement(SlotElement(10, 5), self.size.z)
        stand = CylinderElement(5, 10)

        # Assembler is used to assemble this model
        maker = Assembler.make_with_element(base)
        cutout_maker = maker.make_cutout_sub()
        # made with top side as the plane
        maker.place_element(stand, [Assembler.Place(offset=p) for p in self.stand_centers()])

        # place the holes on the base using the cut mode
        cutout_maker.place_element(hole, [Assembler.Place(offset=p) for p in self.hole_centers()])

        return maker.make_rendering()

    def hole_centers(self) -> list[Vec2]:
        dx = self.size.x / 2 - 10
        dy = self.size.y / 2 - 10
        return [Vec2(x, y) for x in [dx, -dx] for y in [dy, 0, -dy]]

    def stand_centers(self) -> list[Vec2]:
        return [Vec2(x, y) for x in [-10, 10] for y in [0]]


rendering = PlateWithHoles().render()
rendering.show()

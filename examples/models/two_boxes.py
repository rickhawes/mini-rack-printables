from mini_rack_printables import BoxElement, Dir2, Model, Modeler
from mini_rack_printables.core.geometry import AxDir3


class TwoElementModel(Model):
    def render(self) -> Model.Rendering:
        base = BoxElement(30, 20, 10)
        node = BoxElement(2, 1.5, 1)

        # place the nodes on the base using a modeler
        md = Modeler.make_with_element(base, side=AxDir3.Y_PLUS)
        for member in Dir2:
            cut = member.value == Dir2.CORNER_LF_BT.value
            md.place_element(node, Dir2(member.value), cut)

        return md.render()


rendering = TwoElementModel().render()
rendering.show()
# rendering.export("outputs/modeling.step")

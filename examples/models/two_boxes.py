from mini_rack_printables import Assembler, AxDir3, BoxElement, Dir2, Model, Vec3


def render() -> Model.Rendering:
    base = BoxElement(30, 20, 10)
    node = BoxElement(2, 1.5, 1)

    # place the nodes on the base using a assembler
    maker = Assembler.make_with_element(base, side=AxDir3.Y_MINUS)
    # for member in Dir2:
    #     if member.value == Dir2.CORNER_LF_BT.value:
    #         cut = True
    #         offset = Vec3(0, 0, -1)
    #     else:
    #         cut = False
    #         offset = Vec3(0, 0, 0)
    maker.place_element(node, Assembler.Place(origin=Dir2.CENTER))

    return maker.render()


rendering = render()
rendering.show()
rendering.export_step("outputs/two_boxes.step")

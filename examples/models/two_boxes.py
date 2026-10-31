from mini_rack_printables import Assembler, AxDir3, BoxElement, Dir2, Model, Vec3


def render() -> Model.Rendering:
    base = BoxElement(30, 20, 10)
    node = BoxElement(2, 1.5, 1)

    # place a node on the side of a box
    maker = Assembler.make_with_element(base, z_dir=AxDir3.Y_MINUS)
    maker.place_element(node, Assembler.Place(origin=Dir2.Y_PLUS))

    return maker.make_rendering()


rendering = render()
rendering.show()
rendering.export_step("outputs/two_boxes.step")

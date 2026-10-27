from mini_rack_printables import Assembler, BoxElement, Model


def render() -> Model.Rendering:
    bx = BoxElement(20, 20, 10)
    maker = Assembler.make_with_element(bx)
    return maker.render()


rendering = render()
rendering.show()

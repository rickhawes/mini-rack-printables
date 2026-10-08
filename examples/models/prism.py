from mini_rack_printables import BoxElement, Model


class ElementModel(Model):
    def render(self) -> Model.Rendering:
        bx = BoxElement(20, 20, 10)
        part = bx.render()
        return Model.Rendering(part)


rendering = ElementModel().render()
rendering.show()

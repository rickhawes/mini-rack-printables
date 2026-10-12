from mini_rack_printables import BoxElement, Modeler, Model

class ElementModel(Model):
    def render(self, modeler: Modeler) -> None:
        bx = BoxElement(20, 20, 10)
        modeler.place(bx)

md = Modeler()
md.render(ElementModel())
md.show()


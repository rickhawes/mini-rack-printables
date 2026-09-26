class ElementBuilder:
    builder: PartBuilder
    element: Element3D
    part: Part
    plane: Plane



    def add(element: Element3D, how: HowToAdd) -> ElementBuilder:
        self.element = element
        Location 
        self.builder.add()
        return self

    def mirror_last()

def example() -> Part:
    base = BoxElement()
    with base.builder(Side.TOP) as bd: 
        part2 = BoxElement()
        bd.add(part2, place=Place.xxx)
        bd.add_mirror()
        part3 = TrapezoidElement().make_prism()
        bd.add(part3, place=Place.xxx, z_axis=)
        bd.add_mirror()
    return bd.part
        
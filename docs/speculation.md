Top level code

```python
# Create a model
plate = FacePlate(rack_units=1.0)

# Do the rendering stuff
md = Modler(name="Blank")
md.render(plate)
md.show()
md.export_step("outputs/blank_face_plate.step")
```


Model render method for a FacePlate

```python
class FacePlate(Model):
    def render(self, md: Modler) -> None:
        md.place_element(self._render_plate(md), next_plate=Side.TOP)
        if self.ribs:
            rib = _make_rib()
            md.place_element(rib, side_plane=Place.BOTTOM)
            md.mirror_last(Ax.Y)
        if self.features:
            md.place_features(self.features, self.layout, size=Vec2())
        
                
    def _make_rib() -> Element3D:
        trap = TrapazoidElement(...)
        return PrismElement(trap, amount)
        
        
```

Model rendering for a Shelf

```python



class RackShelf(Model):
    def render(self, md: Modler) -> None:
        md.place_element(self._render_plate(md), next_plate=Side.TOP)
        md.place_features(self.features)
        
        # front
        md.save_plate()
        md.place_element(_make_faceplate(), side_plane=Place.BOTTOM, next_plate=Side.TOP)
        md.place_features(self.faceplate_features, self.faceplate_layout, size=Vec())
        md.recall_plate()
    
        # walls
        md.place_element(_make_wall(), side_plane=Place.LEFT)
        md.mirror_last(Ax.X)
        
    
```

```python
class Modler:
    class State(Enum):
        PRE_RENDER
        RENDERING
        POST_RENDER

    state: State  = State.PRE_RENDER
    builder: BuildPart | None = None
    last_element: Element3D | None = None
    plane_element: list[Plane] = []
    plate:
    plane_stack: 
    
    def render(self, model: Model):
        assert state == State.PRE_RENDER
        
        with BuildPart() as bd:
            self.builder = bd
            self.state = State.RENDERING
            model.assemble(self)

        self.builder = None
        self.state = State.POST_RENDER
        self.result = bd.part

    # Rendering Methods

    def next_plate(element, side):
        ...

    def save_plate(self):
        ...

    def recall_plate(self):
        ...

    def place(self, element: Element3D):
        ...

    def stack(self, elements: list[Element3D], dir=):
        ...

    def assemble(self, features: list[ModelFeatures]):
        ...

    # Post Rendering Methods

    def show(self):

    def export(self, ):
    
```

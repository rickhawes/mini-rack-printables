"""Classes to model a 3D printable
"""

from abc import ABC, abstractmethod
from enum import Enum, auto
from dataclasses import dataclass

from build123d import BuildPart, export_step
import ocp_vscode as viewer

from .elements_3d import Element3D
from .geometry import Bx, Place, AxDir
from .feature import Feature

class Model(ABC):
    """
    Base-class for 3d printable models.
    """

    @abstractmethod
    def render(self, modeler: Modeler) -> None:
        """
        Render the model as a shape

        Args:
            modeler (Modeler): the modeler to place elements and shapes into
        """
        pass

class Modeler:
    """The top-level model renderer and exporter

    The modeler serves many roles:
        - For top-level code, the modeler provides a renderer and exporter for models
        - For model code, the modeler assembles and gathers each part of the model into the full model.
        - For core layer code, the modeler encapsulates the build123d Builder classes.

    Example:
        some_model = SomeModel(... with parameters)
        md = Modeler()
        md.render(some_model)
        md.save("filename.stl")

    Attributes:
        state (State): the current state of the model (PRE_RENDER, RENDERING, POST_RENDER)
        base (Bx): the base bounding box of the base plate of the model

    """
    
    class State(Enum):
        """State of the modeler. Each instance only be used rendered once"""
        PRE_RENDER = auto()
        """Initial state before rendering a model"""
        RENDERING = auto()
        """During rendering of a model"""
        POST_RENDER = auto()
        """Rendering complete a model can be viewed and exported"""

    state: State  = State.PRE_RENDER
    """State for the """
    builder: BuildPart | None = None
    """Build123d context which accumulates the rendered parts of the model"""
    base_element: Element3D | None = None
    """The base bounding box on which other """
    last_element: Element3D | None = None
    """Last element placed"""


    def render(self, model: Model) -> None:
        """Render the passed in model into the modeler for export"""
        assert self.state == Modeler.State.PRE_RENDER
        
        with BuildPart() as bd:
            self.builder = bd
            self.state = Modeler.State.RENDERING
            model.render(self)

        self.builder = None
        self.state = Modeler.State.POST_RENDER

    # Rendering methods used by models during rendering
    #
    @dataclass(frozen=True)
    class Placement:
        """Specify the placement of two elements relative to each other.

        Attributes:
            side_on_base: The side of the base box which to place the other box
            place_on_side: The position to place the other box on the base side
            other_dir: The z-direction of the other box
        """
        side_on_base: AxDir = AxDir.PLUS_Z
        place_on_side: Place = Place.CENTER
        other_dir : AxDir = AxDir.PLUS_Z

    def place(self, element: Element3D, placement: Placement) -> None:
        """Place an element """
        element.render()
        self.last_element = element

    def stack(self, elements: list[Element3D], placement:Placement) -> None:
        pass

    def assemble(self, features: list[Feature]):
        pass

    def set_base(self, new_base: Element3D | None) -> Element3D | None:
        old_base = self.base_element
        self.base_element = new_base if new_base is not None else self.last_element
        return old_base


    # Post Rendering Methods

    def show(self) -> None:
        if self.state != Modeler.State.POST_RENDER or self.builder is None or self.builder.part is None:
            raise ValueError("No rendering to show")
        viewer.show(self.builder.part)

    def export(self, filename: str) -> None:
        if self.state != Modeler.State.POST_RENDER or self.builder is None or self.builder.part is None:
            raise ValueError("No rendering to show")
        assert self.builder.part is not None
        export_step(self.builder.part, filename)
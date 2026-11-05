"""Shows a Cutout feature with a rib."""

from mini_rack_printables import Cutout, FaceplateStyle, SlotFigure, feature_xray

cutout = Cutout(SlotFigure(10.0, 5.0), rib=FaceplateStyle.STD_RIB)
model = feature_xray(cutout)

# Show the model in the OCP viewer
model.show()

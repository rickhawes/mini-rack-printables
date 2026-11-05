"""Shows a corner holder feature."""

from mini_rack_printables import CornerHolder, RectangleFigure, feature_xray

holder = CornerHolder(RectangleFigure(100, 100, 5), corner_width=12, corner_height=12)
model = feature_xray(holder)

# Show the model in the OCP viewer
model.show()

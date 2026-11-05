"""Shows a BoxHolder feature."""

from mini_rack_printables import BoxHolder, Vec3, feature_xray

holder = BoxHolder(
    device_size=Vec3(60, 30, 40), device_rounding=1.0, style=BoxHolder.BACK_LIP
)
model = feature_xray(holder)

# Show the model in the OCP viewer
model.show()

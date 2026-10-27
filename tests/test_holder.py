from mini_rack_printables import (
    BoxHolder,
    CornerHolder,
    FeatureXRayModel,
    PuckHolder,
    RectangleElement,
    Vec3,
    ModelLogger,
)


def test_default_holder(viewer_logger: ModelLogger) -> None:
    holder = BoxHolder(device_size=Vec3(30, 20, 20))
    xray = FeatureXRayModel(holder, only_adds=False)
    rendering = xray.render()
    viewer_logger.log(rendering.part)


def test_no_rounding(viewer_logger: ModelLogger) -> None:
    holder = BoxHolder(device_size=Vec3(30, 20, 20), device_rounding=0.0)
    xray = FeatureXRayModel(holder, only_adds=False)
    rendering = xray.render()
    viewer_logger.log(rendering.part)


def test_back_lip(viewer_logger: ModelLogger) -> None:
    holder = BoxHolder(device_size=Vec3(30, 20, 20), style=BoxHolder.BACK_LIP)
    xray = FeatureXRayModel(holder, only_adds=False)
    rendering = xray.render()
    viewer_logger.log(rendering.part)


def test_no_cutout(viewer_logger: ModelLogger) -> None:
    holder = BoxHolder(device_size=Vec3(30, 20, 20), style=BoxHolder.NO_CUTOUT)
    xray = FeatureXRayModel(holder, only_adds=False)
    compound = xray.render()
    rendering = xray.render()
    viewer_logger.log(rendering.part)

def test_puck_holder(viewer_logger: ModelLogger) -> None:
    holder = PuckHolder(device_size=Vec3(80, 20, 80), device_rounding=10)
    xray = FeatureXRayModel(holder, only_adds=False)
    rendering = xray.render()
    viewer_logger.log(rendering.part)


def test_corner_holder(viewer_logger: ModelLogger) -> None:
    holder = CornerHolder(RectangleElement(80, 30, 2))
    xray = FeatureXRayModel(holder, only_adds=False)
    compound = xray.render()
    rendering = xray.render()
    viewer_logger.log(rendering.part)

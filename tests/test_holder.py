from mini_rack_printables import (
    WallHolder,
    XRayModel,
    PuckHolder,
    CornerHolder,
    RectangleElement,
)


def test_default_holder(viewer_logger):
    holder = WallHolder(device_size=(30, 20, 20))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2
    viewer_logger.log(compound)


def test_no_rounding(viewer_logger):
    holder = WallHolder(device_size=(30, 20, 20), device_rounding=0.0)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2
    viewer_logger.log(compound)


def test_back_lip(viewer_logger):
    holder = WallHolder(device_size=(30, 20, 20), style=WallHolder.BACK_LIP)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2
    viewer_logger.log(compound)


def test_no_cutout(viewer_logger):
    holder = WallHolder(device_size=(30, 20, 20), style=WallHolder.NO_CUTOUT)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 1
    viewer_logger.log(compound)


def test_puck_holder(viewer_logger):
    holder = PuckHolder(device_size=(80, 20, 80), device_rounding=10)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2
    viewer_logger.log(compound)


def test_corner_holder(viewer_logger):
    holder = CornerHolder(RectangleElement(80, 30, 2))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 1
    viewer_logger.log(compound)

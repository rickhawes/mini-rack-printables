from mini_rack_printables import WallHolder, XRayModel, PuckHolder, CornerHolder, RectangleElement


def test_default_holder():
    holder = WallHolder(device_size=(30, 20, 20))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_no_rounding():
    holder = WallHolder(device_size=(30, 20, 20), device_rounding=0.0)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_back_lip():
    holder = WallHolder(device_size=(30, 20, 20), style=WallHolder.BACK_LIP)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_no_cutout():
    holder = WallHolder(device_size=(30, 20, 20), style=WallHolder.NO_CUTOUT)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 1


def test_puck_holder():
    holder = PuckHolder(device_size=(100, 20, 100), device_rounding=10)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_corner_holder():
    holder = CornerHolder(RectangleElement(100, 30, 2))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 1

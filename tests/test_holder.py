from mini_rack_printables import Holder, HolderStyle, XRayModel


def test_default_holder():
    holder = Holder(device_size=(30, 20, 20))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_no_rounding():
    holder = Holder(device_size=(30, 20, 20), device_rounding=0.0)
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2


def test_back_lip():
    holder = Holder(HolderStyle.BACK_LIP, device_size=(30, 20, 20))
    xray = XRayModel(holder, only_adds=False)
    compound = xray.render()
    assert len(compound.children) == 2

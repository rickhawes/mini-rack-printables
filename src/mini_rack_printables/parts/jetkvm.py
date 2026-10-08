from .import_feature import ImportFeature


class JetKVM(ImportFeature):
    """
    A cutout part for a holding a Jet KVM.
    """

    def __init__(self) -> None:
        super().__init__(asset="jetkvm_trimmed.brep", cutout=True)

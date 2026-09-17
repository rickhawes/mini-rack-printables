from .import_part import ImportPart


class JetKVM(ImportPart):
    """
    A cutout part for a holding a Jet KVM.
    """

    def __init__(self):
        super().__init__(asset="jetkvm_trimmed.brep", cutout=True)

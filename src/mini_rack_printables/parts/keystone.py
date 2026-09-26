from .import_part import ImportPart


class Keystone(ImportPart):
    """
    A keystone cutout part.
    """

    def __init__(self):
        super().__init__(asset="keystone.brep", cutout=True)

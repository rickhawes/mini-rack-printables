"""Add Network Keystone cutouts to a plate."""
from mini_rack_printables.features.import_feature import ImportFeature


class Keystone(ImportFeature):
    """
    Add Network Keystone cutouts to a plate.
    """

    def __init__(self) -> None:
        super().__init__(asset="keystone.brep", cutout=True)

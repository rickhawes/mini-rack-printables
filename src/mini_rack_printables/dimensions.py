# ------------------------------------------------------------------------------------------------
# Dimensions
#
# Constants for the dimensions of the hardware including 10-inch racks and screws.
#
# ------------------------------------------------------------------------------------------------
from enum import Enum

# ------------------------------------------------
# Rack Dimensions
# ------------------------------------------------

# For the 10 inch rack specification see this file
# https:#upload.wikimedia.org/wikipedia/commons/8/84/19_inch_vs_10_inch_rack_dimensions.svg
#


class RackDims(float, Enum):
    """
    Dimensions for a server rack
    """

    WIDTH_10INCH = 254.0
    """Width of a 10 inch"""
    DEPTH_8INCH = 200
    """Depth of a 8 inch (tecmojo variety"""
    DEPTH_10INCH = 260
    """Depth of a 10 inch (techmojo variety)"""
    HEIGHT_1U = 44.50
    """Height of a 1u rack"""


class RackScrewDims(float, Enum):
    """
    Dimmensions for the rack holes and the
    """

    DX = 236.525
    """Distance between screws along the x-axis (width axis)"""
    BOTTOM = 6.35
    """Distance between the rack slot to bottom screw"""
    BOTTOM_TO_MIDDLE = 15.875
    """Distance between middle and bottom screw hole"""
    MIDDLE = BOTTOM + BOTTOM_TO_MIDDLE
    """Distance between the slot to middle screw hole"""
    TOP = RackDims.HEIGHT_1U - 6.35
    """Distance between the rack slot to top screw holes"""
    MIDDLE_TO_TOP = TOP - MIDDLE
    """Distance between top and middle screw holes"""
    BOTTOM_TO_TOP = BOTTOM_TO_MIDDLE + MIDDLE_TO_TOP
    """Distance between bottom to top screw holes"""
    TOP_LOWER_TO_BOTTOM_UPPER = 12.70
    """Distance between the top of a lower slot and the bottom of a upper slot"""


class ShelfTabDims(float, Enum):
    """
    Dimensions for the tabs on a rack face plate or shelf
    """

    WIDTH_TECMOJO = 19.53
    """Width for a TecMojo shelf"""
    WIDTH_MIN = 15.875
    """Minimal width of the rack tab from the standard"""


# ------------------------------------------------
# Hardware Constants
# ------------------------------------------------


class Screw1032Dims(float, Enum):
    """
    Dimensions for a 10-32 screw
    """

    HOLE = 4.84
    """Hole for 10-32"""
    HEAD = 10.57
    """Head for a 10-32 screw"""

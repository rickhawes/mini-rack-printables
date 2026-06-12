//------------------------------------------------------------------------------------------------
// Dimensions
//
// Constants for the dimensions of the hardware including 10-inch racks and screws.
//
//------------------------------------------------------------------------------------------------

//------------------------------------------------
// Rack Dimensions
//------------------------------------------------
/* [Hidden */

// For the 10 inch rack specification see this file
// https://upload.wikimedia.org/wikipedia/commons/8/84/19_inch_vs_10_inch_rack_dimensions.svg
//

// Width of a 10 inch
rack_width_10inch = 254.0;
// Width of a 19 inch
rack_width_19inch = 482.60;
// Depth of a 10 inch (tecmojo variety)
rack_depth_8inch = 200;
// Depth of a 10 inch (techmojo variety)
rack_depth_10inch = 260;

// Distance between screws along the x-axis (width axis)
rack_screw_dx_10inch = 236.525;
// Distance between screws along the x-axis (width axis)
rack_screw_dx_19inch = 465.12;

// Height of a 1u rack
rack_1u_height = 44.50;

// Distance between the slot to bottom screw
rack_screw_dy_bottom = 6.35;
// Distance between middle and bottom screw hole 
rack_screw_dy_bottom_middle = 15.875;
// Distance between the slot to middle screw 
rack_screw_dy_middle = rack_screw_dy_bottom + rack_screw_dy_bottom_middle; // not equal to rack_1u_height/2
// Distance between the slot to top screw
rack_screw_dy_top = rack_1u_height - 6.35;
// Distance between middle and top screw hole
rack_screw_dy_middle_top = rack_screw_dy_top - rack_screw_dy_middle;
// Distance between top and bottom screw holes
rack_screw_dy_bottom_top = rack_screw_dy_bottom_middle + rack_screw_dy_middle_top;
// Distance between bottom of one slot and the top of the lower rack
rack_screw_dy_top_bottom = 12.70;

// Width of the rack tab for a tecmojo rack
shelf_tab_width_tecmojo = 19.53; 
// Minimal width of the rack tab from the standard
shelf_tab_width_min = 15.875;




//------------------------------------------------
// Hardware Constants
//------------------------------------------------

// 10-24 screw hole diameter
screw_hole_10_24 = 4.84;
// 10-24 screw head diameter
screw_head_10_24 = 10.57;


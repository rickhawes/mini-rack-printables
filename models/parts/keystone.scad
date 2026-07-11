// Keystone part
//
// This part is a keystone jack holder
// 
// Credits: https://github.com/spuder/10-Inch-Rack-OpenSCAD/blob/main/KeystoneJack.scad
// License: CC-BY-SA 4.0

include <BOSL2/std.scad>
include <../geometry.scad>
include <../shapes.scad>
include <part_base.scad>

//------------------------------------------------
// Part Constants
//------------------------------------------------
/* [Hidden] */

// value for the type of a part
KEYSTONE_TYPE     = "keystone";

// Dimensions for the keystone jack holder
e=0.01; // epsilon for coplanar face fixes, fixes bug where some faces leave a thin sliver of material
wall=2.5;
front_hole_width=14.9;
front_hole_height=16.3;
front_hole_z_offset=4.28;
front_hole_lip=0;

jack_width=front_hole_width+wall;
jack_height=25;
jack_depth=9.7;
front_large_catch_depth=3;
front_chamfer_angle=50; // degrees from horizontal (depth axis)

back_hole_height=24.4;
back_hole_z_offset=1.9;

back_small_catch_length=2;
back_small_catch_depth=1.4;

back_large_catch_length=2.6;
back_large_catch_depth=1.3;

back_chamfer=1.2;

keystone_size = [jack_width+wall, jack_height+wall, jack_depth];


//------------------------------------------------
// Functions and modules
//------------------------------------------------
function keystone(
    align = CENTER,
    padding = 0,
    shift = [0,0]
) = 
    assert(is_padding(padding))
    let(
        cutout_rc = rc(keystone_size),
        outset_rc = apply_padding(cutout_rc, padding)
    )
    part_base(
        KEYSTONE_TYPE, 
        align, 
        padding, 
        shift, 
        layout_size=rc_size(outset_rc)
    );


function is_keystone(part)    = part_type(part) == KEYSTONE_TYPE;


cross_section_preview=true;
module _render_keystone(part, plate_size) {
    module keystone_geometry() {
        union(){
            difference(){
                // Make solid cube
                cube([jack_width+wall,jack_depth,jack_height+wall]);
            // Cut out the front hole
            translate([(jack_width+wall-front_hole_width)/2,0,front_hole_z_offset])
                color("blue")
                cube([front_hole_width,jack_depth+wall,front_hole_height]);
            // Cut out the back hole. It should be extruded to front_large_catch_depth
            translate([(jack_width+wall-front_hole_width)/2,front_large_catch_depth,back_hole_z_offset])
                color("red")
                cube([front_hole_width,jack_depth+wall-front_large_catch_depth,back_hole_height]);

            // Cut out chamfer on front face of small catch
            color("green")
            translate([wall + front_hole_width, 0, 0])
                rotate([0, -90, 0])
                    linear_extrude(front_hole_width)
                        polygon([
                            [front_hole_z_offset + front_hole_height - e, front_hole_lip - e],          // A: shifted e below catch floor to avoid coplanar artifact
                            [front_hole_z_offset + front_hole_height + (front_large_catch_depth - front_hole_lip) * tan(front_chamfer_angle), front_large_catch_depth],  // B: angle-derived point
                            [front_hole_z_offset + front_hole_height - e, front_large_catch_depth]      // C: inner corner, same e shift as A
                        ]);

            // Cut out chamefer on front face of large catch
            // color("orange")
            // translate([wall + front_hole_width, 0, 0])
            //     rotate([0, -90, 0])
            //         linear_extrude(front_hole_width)
            //             polygon([
            //                 [front_hole_z_offset+e, front_hole_lip],  // A: front face, bottom of front hole
            //                 [back_hole_z_offset,  front_large_catch_depth],     // B: inner ledge, bottom of back hole
            //                 [front_hole_z_offset, front_large_catch_depth]      // C: inner ledge, same Z as A
            //             ]);

            // Front directional triangle emboss (cut into face)
            color("yellow")
                translate([(jack_width+wall)/2, 0.4, (front_hole_z_offset + front_hole_height + jack_height + wall) / 2])
                    rotate([90, 0, 0])
                        linear_extrude(height = 0.4+e)
                            polygon([
                                [0, -2],
                                [-2, 2],
                                [2, 2]
                            ]);

            // Chamfer back bottom edge (along X)
            translate([jack_width+wall+e, 0, -e])
                rotate([0, -90, 0])
                    linear_extrude(jack_width+wall+2*e)
                        polygon([[-e, jack_depth+e], [back_chamfer, jack_depth+e], [-e, jack_depth-back_chamfer]]);

            // Chamfer back top edge (along X)
            translate([jack_width+wall+e, 0, -e])
                rotate([0, -90, 0])
                    linear_extrude(jack_width+wall+2*e)
                        polygon([[jack_height+wall+2*e, jack_depth+e], [jack_height+wall+2*e-back_chamfer, jack_depth+e], [jack_height+wall+2*e, jack_depth-back_chamfer]]);

            // Chamfer back left edge (along Z)
            translate([0, 0, -e])
                linear_extrude(jack_height+wall+2*e)
                    polygon([[-e, jack_depth+e], [back_chamfer, jack_depth+e], [-e, jack_depth-back_chamfer]]);

            // Chamfer back right edge (along Z)
            translate([0, 0, -e])
                linear_extrude(jack_height+wall+2*e)
                    polygon([[jack_width+wall+e, jack_depth+e], [jack_width+wall+e-back_chamfer, jack_depth+e], [jack_width+wall+e, jack_depth-back_chamfer]]);

            } // end difference

            // Small back catch (added geometry)
            color("purple")
                translate([wall + front_hole_width, 0, 0])
                    rotate([0, -90, 0])
                        linear_extrude(front_hole_width)
                            polygon([
                                [back_hole_z_offset + back_hole_height - back_small_catch_length, jack_depth - back_small_catch_depth],  // A
                                [back_hole_z_offset + back_hole_height,                           jack_depth - back_small_catch_depth],  // B
                                [back_hole_z_offset + back_hole_height,                           jack_depth],                           // C
                                [back_hole_z_offset + back_hole_height - back_small_catch_length, jack_depth]                            // D
                            ]);

            // Large back catch (added geometry)
            color("cyan")
                translate([wall + front_hole_width, 0, 0])
                    rotate([0, -90, 0])
                        linear_extrude(front_hole_width)
                            polygon([
                                [back_hole_z_offset,                           jack_depth - back_large_catch_depth],  // A
                                [back_hole_z_offset + back_large_catch_length, jack_depth - back_large_catch_depth],  // B
                                [back_hole_z_offset + back_large_catch_length, jack_depth],                           // C
                                [back_hole_z_offset,                           jack_depth]                            // D
                            ]);

        } // end union
    }
    // Cutout for the keystone 
    tag("remove")
    translate([-keystone_size.x/2, -keystone_size.y/2, -plate_size.z])
    cube([keystone_size.x, keystone_size.y, keystone_size.z]);

    // Drop the part into the center of the plate, and rotate it to be oriented correctly
    tag("keep")
    translate([-keystone_size.x/2, -keystone_size.y/2, -plate_size.z/2]) 
    // Flip entire part because I accidentially desinged it upside down
    mirror([1, 0, 0])
    rotate([90, 0, 180])
    keystone_geometry();
}

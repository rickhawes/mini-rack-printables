include <BOSL2/std.scad>
include <../models/parts/render_part.scad>

// An simple assembly to test rendering of parts
module test_render_part(part, section_size) {
    with_part_rendering(part, section_size) {
        cube(section_size, center=true);
    }
}
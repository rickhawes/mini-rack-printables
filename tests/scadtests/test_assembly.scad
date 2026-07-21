include <BOSL2/std.scad>
include <../models/parts/render_part.scad>

// An simple assembly to test rendering of parts
module test_render_part(part, section_size) {
    diff() {
        cube(section_size, center=true) {
            children();
        }
    }
}
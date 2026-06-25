include <BOSL2/std.scad>
include <../models/render_part.scad>

// An simple assembly to test rendering of parts
module test_render_part(part, section_size) {
    diff(remove=REMOVE_TAG) {
        cube(section_size) {
            // Parts
            if (!is_undef(part)) {
                render_part(part, section_size);
            }
        }
    }
}
// Example part created with an STL file that has been trimmed and measured
// In this case, it is a holder for a JetKVM kvm controller
//
include <../main.scad>

function jetkvm() = stl(
    file = "jetkvm_trimmed.stl", 
    size = [44.2386,38.4583,33.1579],
    center_adjust = [0,0,1.75],
);

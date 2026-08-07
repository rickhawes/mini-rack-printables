#!/usr/bin/env python3
import build123d as bd
import argparse


def convert_stl_to_brep(input_path: str, output_path: str):
    importer = bd.Mesher(unit=bd.Unit.MM)
    full_mesh = importer.read(input_path)[0]
    center = bd.Shape.combined_center([full_mesh], center_of=bd.CenterOf.BOUNDING_BOX)
    centered_mesh = full_mesh.move(bd.Location((-center.X, -center.Y, -center.Z)))
    bd.export_brep(centered_mesh, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert STL to BREP")
    parser.add_argument("input", help="Input STL file path")
    parser.add_argument("output", help="Output BREP file path")
    args = parser.parse_args()
    convert_stl_to_brep(args.input, args.output)

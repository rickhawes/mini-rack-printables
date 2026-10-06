#!/usr/bin/env python3
import build123d as bd
from typing import cast

import argparse


def convert_stl_to_brep(input_path: str, output_path: str):
    importer = bd.Mesher(unit=bd.Unit.MM)
    full_mesh = importer.read(input_path)[0]
    center = bd.Shape.combined_center([full_mesh], center_of=bd.CenterOf.BOUNDING_BOX)  # pyright: ignore[reportPrivateImportUsage]
    centered_mesh = full_mesh.move(bd.Location((-center.X, -center.Y, -center.Z)))
    _ = bd.export_brep(centered_mesh, output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert STL to BREP")
    _ = parser.add_argument("input", help="Input STL file path", type=str)
    _ = parser.add_argument("output", help="Output BREP file path", type=str)
    args = parser.parse_args()
    convert_stl_to_brep(cast(str, args.input), cast(str, args.output))

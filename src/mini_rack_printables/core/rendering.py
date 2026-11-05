"""Rendering of a 3D printable model.

See Also:
    `faceplate` - Example model
"""

from dataclasses import dataclass

import build123d as bd
import ocp_vscode as viewer


@dataclass(frozen=True)
class Rendering:
    """The rendering of a model function and the operations that can be performed."""

    part: bd.Part | bd.Compound

    def show(self) -> None:
        """Show the rendering in the OCP Viewer."""
        viewer.show(self.part)

    def export_step(self, filename: str) -> None:
        """Export the rendering into a STEP file."""
        if not bd.export_step(self.part, filename):
            raise IOError("File not saved")

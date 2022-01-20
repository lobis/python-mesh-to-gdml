import unittest

import os

from stl.mesh import Mesh

from ..src.mesh2gdml import Stl


class TestMeshFromFile(unittest.TestCase):
    files_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../files"))

    def test_files_dir_exists(self):
        self.assertTrue(os.path.isdir(self.files_dir), f"files directory '{self.files_dir}' does not exist")

    def test_mesh_from_file_cube(self):
        stl_file = os.path.join(self.files_dir, "cube.ascii.stl")
        self.assertTrue(os.path.isfile(stl_file))

        mesh = Stl.from_file(stl_file)

        self.assertEqual(len(mesh.faces), 12)  # cube has 12 triangular faces (2 per side)

    def test_mesh_from_file_cylinder(self):
        stl_file = os.path.join(self.files_dir, "cylinder.stl")
        self.assertTrue(os.path.isfile(stl_file))

        mesh = Stl.from_file(stl_file)

        self.assertEqual(len(mesh.faces), 636)  # cylinder has 636 triangular faces for this mesh refinement


if __name__ == '__main__':
    unittest.main()

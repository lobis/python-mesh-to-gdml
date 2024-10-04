import os
import pytest
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from mesh2gdml import Stl


files_dir = os.path.abspath(os.path.join(os.path.realpath(__file__), "../../files"))


@pytest.fixture
def cube_file():
    return os.path.join(files_dir, "cube.ascii.stl")


@pytest.fixture
def cylinder_file():
    return os.path.join(files_dir, "cylinder.stl")


def test_files_dir_exists():
    assert os.path.isdir(files_dir), f"files directory '{files_dir}' does not exist"


def test_mesh_from_file_cube(cube_file):
    assert os.path.isfile(cube_file)

    mesh = Stl.from_file(cube_file)

    assert len(mesh.faces) == 12  # cube has 12 triangular faces (2 per side)


def test_mesh_from_file_cylinder(cylinder_file):
    assert os.path.isfile(cylinder_file)

    mesh = Stl.from_file(cylinder_file)

    assert (
        len(mesh.faces) == 636
    )  # cylinder has 636 triangular faces for this mesh refinement

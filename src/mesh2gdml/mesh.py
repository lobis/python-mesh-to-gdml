import numpy as np


class Mesh:
    # We store a mesh as a list of points and a list of triangular faces

    def __init__(self, vertices=None, faces=None, validate=True):
        if faces is None:
            faces = []
        if vertices is None:
            vertices = []

        self.vertices = np.array(vertices, dtype=np.float32)
        self.faces = np.array(faces, dtype=np.int32)

        if validate:
            unique_vertex_indices = np.unique(self.faces)
            assert len(unique_vertex_indices) == len(vertices)
            comparison = unique_vertex_indices == np.arange(len(vertices))
            assert comparison.all()

    def __repr__(self):
        return f"vertices:\n{self.vertices}\nfaces:\n{self.faces}"

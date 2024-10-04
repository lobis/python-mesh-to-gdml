import numpy as np

from .mesh import Mesh

import numpy
import os

# https://en.wikipedia.org/wiki/STL_(file_format)#Binary_STL
HEADER_SIZE_BYTES = 80
TRIANGLE_COUNT_SIZE = 4
VECTOR_SIZE_BYTES = 12
ATTRIBUTE_SIZE_BYTES = 2


class Stl(Mesh):
    @classmethod
    def __vertices_to_mesh(cls, vectors):
        assert len(vectors) % 3 == 0
        assert vectors.shape[1] == 3

        # Using numpy.unique gives error for large STLs possibly because of rounding errors
        vertices = np.zeros([int(len(vectors)), 3], dtype=np.float32)
        faces = np.zeros([int(len(vectors) / 3), 3], dtype=np.uint32)

        aux_hash_map = dict()

        counter = 0
        for i, vector in enumerate(vectors):
            vector_hash = vector.data.tobytes()
            if vector_hash not in aux_hash_map:
                vertices[counter, :] = vector
                aux_hash_map[vector_hash] = counter
                counter += 1

            faces[int(np.floor(i / 3)), i % 3] = aux_hash_map[vector_hash]

        print(len(aux_hash_map))
        return vertices[0:counter, :], faces

    @classmethod
    def __from_ascii(cls, file_handle):
        lines = file_handle.readlines()
        # first line should be start with "solid"
        header = lines[0]
        if not header.lstrip().lower().startswith(b"solid"):
            raise Exception("bad stl")
        # last line should end with "endsolid"
        footer = lines[-1]
        if not footer.lstrip().lower().startswith(b"endsolid"):
            raise Exception("bad stl end")

        sequence = [
            b"facet normal",
            b"outer loop",
            b"vertex",
            b"vertex",
            b"vertex",
            b"endloop",
            b"endfacet",
        ]
        assert (len(lines) - 2) % len(sequence) == 0
        triangle_count = int((len(lines) - 2) / len(sequence))

        vectors = np.zeros([triangle_count * 3, 3], dtype=np.float32)

        counter = 0
        for i, line in enumerate(lines[1:-1]):
            if not line.lstrip().lower().startswith(sequence[i % len(sequence)]):
                raise Exception("bad stl")

            if i % len(sequence) in [2, 3, 4]:  # vertex
                vertex_string = line.lower().lstrip().lstrip(b"vertex").rstrip(b"\n")
                vectors[counter, :] = numpy.fromstring(vertex_string, sep=" ")
                counter += 1

        assert len(vectors) == counter

        vertices, faces = cls.__vertices_to_mesh(vectors)
        return cls(vertices=vertices, faces=faces)

    @classmethod
    def __from_binary(cls, file_handle):
        file_handle.read(HEADER_SIZE_BYTES)  # Header
        triangle_count = int.from_bytes(
            file_handle.read(TRIANGLE_COUNT_SIZE), byteorder="little"
        )
        file_handle.seek(0, os.SEEK_END)
        triangle_count_expected = (
            file_handle.tell() - HEADER_SIZE_BYTES - TRIANGLE_COUNT_SIZE
        ) / (4 * VECTOR_SIZE_BYTES + ATTRIBUTE_SIZE_BYTES)

        assert triangle_count == triangle_count_expected
        file_handle.seek(HEADER_SIZE_BYTES + TRIANGLE_COUNT_SIZE)

        vectors = np.zeros([triangle_count * 3, 3], dtype=np.float32)
        counter = 0
        for i in range(triangle_count):
            file_handle.read(VECTOR_SIZE_BYTES)  # facet normal
            for k in range(3):
                vectors[counter, :] = numpy.frombuffer(
                    file_handle.read(VECTOR_SIZE_BYTES), dtype=np.float32
                )
                counter += 1

            file_handle.read(ATTRIBUTE_SIZE_BYTES)

        assert len(vectors) == counter

        vertices, faces = cls.__vertices_to_mesh(vectors)
        return cls(vertices=vertices, faces=faces)

    @classmethod
    def from_file(cls, file_name):
        # file can be binary or ASCII
        with open(file_name, "rb") as file_handle:
            # Check if its binary or ASCII STL
            header = file_handle.read(HEADER_SIZE_BYTES)
            file_handle.seek(0, 0)

            def is_header_binary(file_header):
                for string in [b"\x00", b"STLB"]:
                    if string.lower() in file_header.lower():
                        return True
                return False

            if is_header_binary(header):
                # we consider it an ASCII STL, probably not the best way to do this
                return cls.__from_binary(file_handle)
            else:
                return cls.__from_ascii(file_handle)

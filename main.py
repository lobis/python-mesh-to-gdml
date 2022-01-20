from stl.mesh import Mesh

import xml.etree.cElementTree as ET


# import xmlschema


def process_mesh(mesh, name):
    print("processing mesh...")
    root = ET.Element("gdml",
                      **{"xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                         "xsi:noNamespaceSchemaLocation": "https://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd"}
                      )

    define = ET.SubElement(root, "define")
    materials = ET.SubElement(root, "materials")
    solids = ET.SubElement(root, "solids")
    structure = ET.SubElement(root, "structure")

    tessellated = ET.SubElement(solids, "tessellated", name=f"{name}_solid", aunit="deg", lunit="mm")

    volume = ET.SubElement(structure, "volume", name=f"{name}_volume")
    ET.SubElement(volume, "materialref", ref="G4_Pb")
    ET.SubElement(volume, "solidref", ref=f"{name}_solid")

    def serialize_vertex(three_vector):
        assert len(three_vector) == 3
        result = dict()
        for i, x_i in enumerate(["x", "y", "z"]):
            result[x_i] = f"{three_vector[i]}"
        return result

    vertices_to_name = dict()  # numpy array is not hashable, so we convert to string
    for triangle in mesh.vectors:
        face_vertices = {}
        for vertex in triangle:
            vertex_hash = vertex.data.tobytes()
            if vertex_hash not in vertices_to_name:
                vertices_to_name[vertex_hash] = f"{name}_v{len(vertices_to_name)}"
                ET.SubElement(define, "position", name=vertices_to_name[vertex_hash], unit="mm",
                              **serialize_vertex(vertex))

            face_vertices[f"vertex{len(face_vertices) + 1}"] = vertices_to_name[vertex_hash]
        ET.SubElement(tessellated, "triangular", **face_vertices)

    # world
    world_solid = ET.SubElement(solids, "box", name="world_solid", x="100", y="100", z="100")
    world_volume = ET.SubElement(structure, "volume", name="world")
    physical_volume = ET.SubElement(world_volume, "physvol", name=name)
    ET.SubElement(physical_volume, "volumeref", ref=f"{name}_volume")

    ET.SubElement(world_volume, "materialref", ref="G4_AIR")
    ET.SubElement(world_volume, "solidref", ref="world_solid")

    setup = ET.SubElement(root, "setup", name="Default", version="1.0")
    ET.SubElement(setup, "world", ref="world")

    print("processing mesh done!")

    return ET.ElementTree(root)


def main():
    print("starting...")
    mesh = Mesh.from_file("files/cube.ascii.stl")

    tree = process_mesh(mesh, "mesh")
    ET.indent(tree)

    # schema = xmlschema.XMLSchema("https://service-spi.web.cern.ch/service-spi/app/releases/GDML/schema/gdml.xsd")
    # print(schema.is_valid(tree))

    tree.write("mesh.gdml", encoding="UTF-8", xml_declaration=True)

    print("done!")


if __name__ == '__main__':
    main()

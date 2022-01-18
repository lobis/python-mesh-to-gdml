from stl.mesh import Mesh

import xml.etree.cElementTree as ET


def main():
    print("starting...")
    mesh = Mesh.from_file("files/cube.stl")

    root = ET.Element("gdml")
    define = ET.SubElement(root, "define")
    solids = ET.SubElement(root, "solids")
    tessellated = ET.SubElement(solids, "tessellated", name="cube", aunit="deg", lunit="mm")

    for i, triangle in enumerate(mesh.vectors):
        # print(item)
        for j, vertex in enumerate(triangle):
            ET.SubElement(define, "position", name=f"pos_{i}_{j}", unit="mm",  #
                          x=str(round(vertex[0])), y=str(round(vertex[0])), z=str(round(vertex[0]))
                          )
        ET.SubElement(tessellated, "triangular", vertex1=f"pos_{i}_0", vertex2=f"pos_{i}_1", vertex3=f"pos_{i}_2")

    tree = ET.ElementTree(root)
    ET.indent(tree)

    tree.write("cube.xml")

    print("done!")


if __name__ == '__main__':
    main()

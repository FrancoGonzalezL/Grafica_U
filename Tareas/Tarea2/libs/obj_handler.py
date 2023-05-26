from libs.basic_shapes import Shape


def read_face_vertex(face_description):

    aux = face_description.split('/')

    assert len(aux[0]), "Vertex index has not been defined."

    face_vertex = [int(aux[0]), None, None]

    assert len(aux) == 3, "Only faces where its vertices require 3 indices are defined."

    if len(aux[1]) != 0:
        face_vertex[1] = int(aux[1])

    if len(aux[2]) != 0:
        face_vertex[2] = int(aux[2])

    return face_vertex


def read_OBJ(filename, color):

    vertices = []
    normals = []
    tex_coords = []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(' ')

            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                tex_coords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)
                faces += [[read_face_vertex(face_vertex) for face_vertex in aux[1:4]]]
                for i in range(3, N-1):
                    faces += [[read_face_vertex(face_vertex) for face_vertex in [aux[i], aux[i+1], aux[1]]]]

        vertex_data = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0, 3):
                vertex = vertices[face[i][0]-1]
                normal = normals[face[i][2]-1]

                vertex_data += [
                    vertex[0], vertex[1], vertex[2],
                    color[0],  color[1],  color[2],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3
    return Shape(vertex_data, indices)


def read_OBJ2(filename):

    vertices = []
    normals = []
    tex_coords = []
    faces = []

    with open(filename, 'r') as file:
        for line in file.readlines():
            aux = line.strip().split(' ')

            if aux[0] == 'v':
                vertices += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vn':
                normals += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'vt':
                assert len(aux[1:]) == 2, "Texture coordinates with different than 2 dimensions are not supported"
                tex_coords += [[float(coord) for coord in aux[1:]]]

            elif aux[0] == 'f':
                N = len(aux)
                faces += [[read_face_vertex(face_vertex) for face_vertex in aux[1:4]]]
                for i in range(3, N-1):
                    faces += [[read_face_vertex(face_vertex) for face_vertex in [aux[i], aux[i+1], aux[1]]]]

        vertex_data = []
        indices = []
        index = 0

        # Per previous construction, each face is a triangle
        for face in faces:

            # Checking each of the triangle vertices
            for i in range(0, 3):
                vertex = vertices[face[i][0]-1]
                texture = tex_coords[face[i][1]-1]
                normal = normals[face[i][2]-1]

                vertex_data += [
                    vertex[0], vertex[1], vertex[2],
                    texture[0], texture[1],
                    normal[0], normal[1], normal[2]
                ]

            # Connecting the 3 vertices to create a triangle
            indices += [index, index + 1, index + 2]
            index += 3

    return Shape(vertex_data, indices)

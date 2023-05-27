
# coding=utf-8
"""Vertices and indices for a variety of simple shapes"""

import math
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from libs.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"

# A simple class container to store vertices and indices that define a shape
class Shape:
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = indices

    def __str__(self):
        return "vertices: " + str(self.vertices) + "\n"\
            "indices: " + str(self.indices)

    


def merge(destinationShape, strideSize, sourceShape):

    # current vertices are an offset for indices refering to vertices of the new shape
    offset = len(destinationShape.vertices)
    destinationShape.vertices += sourceShape.vertices
    destinationShape.indices += [(offset/strideSize) + index for index in sourceShape.indices]


def applyOffset(shape, stride, offset):

    numberOfVertices = len(shape.vertices)//stride

    for i in range(numberOfVertices):
        index = i * stride
        shape.vertices[index]     += offset[0]
        shape.vertices[index + 1] += offset[1]
        shape.vertices[index + 2] += offset[2]


def scaleVertices(shape, stride, scaleFactor):

    numberOfVertices = len(shape.vertices) // stride

    for i in range(numberOfVertices):
        index = i * stride
        shape.vertices[index]     *= scaleFactor[0]
        shape.vertices[index + 1] *= scaleFactor[1]
        shape.vertices[index + 2] *= scaleFactor[2]


def createAxis(length=1.0):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #    positions        colors
        -length,  0.0,  0.0, 0.0, 0.0, 0.0,
         length,  0.0,  0.0, 1.0, 0.0, 0.0,

         0.0, -length,  0.0, 0.0, 0.0, 0.0,
         0.0,  length,  0.0, 0.0, 1.0, 0.0,

         0.0,  0.0, -length, 0.0, 0.0, 0.0,
         0.0,  0.0,  length, 0.0, 0.0, 1.0]

    # This shape is meant to be drawn with GL_LINES,
    # i.e. every 2 indices, we have 1 line.
    indices = [
         0, 1,
         2, 3,
         4, 5]

    return Shape(vertices, indices)






#version modificada para la tarea
def createTextureNormalsCube(lnx,lny,tnx,tny):#l lados, t arriba

    # Defining locations,texture coordinates and normals for each vertex of the shape  
    vertices = [
    #   positions            tex coords   normals
    # Z+
        -0.5, -0.5,  0.5,    0, 0,       0,0,1,
         0.5, -0.5,  0.5,    lnx, 0,         0,0,1,
         0.5,  0.5,  0.5,    lnx,   lny,         0,0,1,
        -0.5,  0.5,  0.5,    0,   lny,       0,0,1,   


    #cara no visible
    # Z-          
        -0.5, -0.5, -0.5,    0,  0,          0,0,-1,
         0.5, -0.5, -0.5,    lnx, 0,         0,0,-1,
         0.5,  0.5, -0.5,    lnx, lny,       0,0,-1,
        -0.5,  0.5, -0.5,    0,  lny,        0,0,-1,
       
    #cara no visible
    # X+          
         0.5, -0.5, -0.5,    0,  0,          1,0,0,
         0.5,  0.5, -0.5,    lnx, 0,         1,0,0,
         0.5,  0.5,  0.5,    lnx, lny,       1,0,0,
         0.5, -0.5,  0.5,    0,  lny,        1,0,0,   


    # X-          
        -0.5, -0.5, -0.5,    0,   0,        -1,0,0,
        -0.5,  0.5, -0.5,    0,   lny,      -1,0,0,
        -0.5,  0.5,  0.5,    lnx, lny,      -1,0,0,
        -0.5, -0.5,  0.5,    lnx, 0,        -1,0,0,   


    # Y+          
        -0.5,  0.5, -0.5,    0,  0,        0,1,0,
         0.5,  0.5, -0.5,    0, tny,       0,1,0,
         0.5,  0.5,  0.5,    tnx, tny,         0,1,0,
        -0.5,  0.5,  0.5,    tnx,  0,          0,1,0,   



    #cara no visible
    # Y-          
        -0.5, -0.5, -0.5,    0, 1,          0,-1,0,
         0.5, -0.5, -0.5,    1, 1,          0,-1,0,
         0.5, -0.5,  0.5,    1, 0,          0,-1,0,
        -0.5, -0.5,  0.5,    0, 0,          0,-1,0
        ]   

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [
          0, 1, 2, 2, 3, 0, # Z+
          7, 6, 5, 5, 4, 7, # Z-
          8, 9,10,10,11, 8, # X+
         15,14,13,13,12,15, # X-
         19,18,17,17,16,19, # Y+
         20,21,22,22,23,20] # Y-

    return Shape(vertices, indices)
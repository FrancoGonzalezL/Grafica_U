from libs.scene_graph import SceneGraphNode
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from libs.obj_handler import read_OBJ2
from libs.basic_shapes import createTextureNormalsCube
from libs.shaders import textureSimpleSetup

from OpenGL.GL import *

import libs.transformations as tr
import numpy as np

ASSETS = {
    "nave" :   getAssetPath("nave.obj"),
    "among" : getAssetPath("Among.obj"),
    "pochita": getAssetPath("pochita3.obj"),
    "roca":   getAssetPath("roca.obj"),

    "pochita_text":  getAssetPath("pochita.png"),
    "ladrillo_text":     getAssetPath("ladrillo_text.png"),
    "nave_text":     getAssetPath("nave_text.png"),
    "among_text":    getAssetPath("among2.png"),
    "pasto_text":    getAssetPath("pasto_text.jpg"),

    "black":       getAssetPath("BLACK.jpg"),
    "red":         getAssetPath("RED.png"),
    "blue":        getAssetPath("BLUE.jpg"),
}

def textura(text):
    return textureSimpleSetup(ASSETS[text], GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

def grafo(controller,pipeline,muros,meteorit):

    gpuSuelo     = createGPUShape(pipeline, createTextureNormalsCube(1,1,controller.dim/2 + 30/2,controller.dim/2+200/2))
    gpuNave      = createGPUShape(pipeline, read_OBJ2(ASSETS["nave"]))
    gpuPilar     = createGPUShape(pipeline, read_OBJ2(ASSETS["roca"]))
    gpuAmong1    = createGPUShape(pipeline, read_OBJ2(ASSETS["among"]))
    gpuAmong2    = createGPUShape(pipeline, read_OBJ2(ASSETS["among"]))
    gpuPochita   = createGPUShape(pipeline, read_OBJ2(ASSETS["pochita"]))
    gpuSombra    = createGPUShape(pipeline, read_OBJ2(ASSETS["nave"]))
    gpuMuro      = np.zeros(muros.total, dtype=object)

    
    gpuSuelo.texture     = textura("pasto_text")
    gpuNave.texture      = textura("blue") 
    gpuPilar.texture     = textura("ladrillo_text")
    gpuAmong1.texture    = textura("red")
    gpuAmong2.texture    = textura("blue")
    gpuPochita.texture   = textura("pochita_text")
    gpuSombra.texture    = textura("black")

    for i in range(muros.total):
        gpuMuro[i]         = createGPUShape(pipeline, createTextureNormalsCube(1/4, muros.posiciones[i][2]/4, muros.posiciones[i][2]/4, 1/4))
        gpuMuro[i].texture = textura("ladrillo_text")
#-----------------------------------
    navemodelo = SceneGraphNode("navemodelo")    
    navemodelo.transform = tr.matmul([tr.rotationY(np.pi/2), tr.uniformScale(0.08)])
    navemodelo.childs = [gpuNave]

    naves = SceneGraphNode("naves")
    naves.transform = tr.identity()
    naves.childs = []
#-----------------------------------
    nave = np.zeros(controller.total_boids, dtype=object)
    for i in range(len(nave)):
        nave[i] = SceneGraphNode("nave"+str(i))
        nave[i].transform = tr.identity()
        nave[i].childs += [navemodelo]
        naves.childs   += [nave[i]]
#-----------------------------------
    among1 = SceneGraphNode("among1")
    among1.childs += [gpuAmong1]

    pochita = SceneGraphNode("pochita")
    pochita.childs += [gpuPochita]

    among2 = SceneGraphNode("among2")
    among2.childs += [gpuAmong2]
#-----------------------------------
    textsuelo = SceneGraphNode("textSuelo")
    textsuelo.transform = tr.matmul([tr.translate(controller.dim/2,0.0,controller.dim/2),
                                     tr.scale(controller.dim+200, 0.01, controller.dim+30)])
    textsuelo.childs += [gpuSuelo]
    suelo = SceneGraphNode("suelo")
    suelo.childs += [textsuelo]
    suelo.childs += [pochita]
    suelo.childs += [among1]
    suelo.childs += [among2]
#-----------------------------------
    murosL = np.zeros(len(muros.posiciones),dtype=object)
    for i in range(len(muros.posiciones)):
        murosL[i] = SceneGraphNode("pilar"+str(i))
        murosL[i].transform = tr.matmul([tr.translate(muros.posiciones[i][0],
                                                      muros.posiciones[i][2]/2,
                                                      muros.posiciones[i][1]),
                                        tr.scale(1.0, muros.posiciones[i][2], 1.0)])
        murosL[i].childs += [gpuMuro[i]]
        suelo.childs += [murosL[i]]

    meteoritos = np.zeros(meteorit.total, dtype=object)
    for i in range(meteorit.total):
        meteoritos[i] = SceneGraphNode("meteorito"+str(i))
        meteoritos[i].childs += [gpuPilar]
        suelo.childs += [meteoritos[i]]
#----------------------------------- 
    escena = SceneGraphNode("escena")
    escena.childs = [naves]
    escena.childs += [suelo]
#----------------------------------- 

    return escena
        
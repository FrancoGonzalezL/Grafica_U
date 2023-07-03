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
    return textureSimpleSetup(ASSETS[text], GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

def grafo(controller,pipeline,muros,meteorit):

    gpuSuelo     = createGPUShape(pipeline, createTextureNormalsCube(1,1,controller.anchoMapa/2 + 30/2,controller.largoMapa/2+200/2))
    gpuNave      = createGPUShape(pipeline, read_OBJ2(ASSETS["nave"]))
    gpuPilar     = createGPUShape(pipeline, read_OBJ2(ASSETS["roca"]))
    gpuAmong1    = createGPUShape(pipeline, read_OBJ2(ASSETS["among"]))
    gpuAmong2    = createGPUShape(pipeline, read_OBJ2(ASSETS["among"]))
    gpuPochita   = createGPUShape(pipeline, read_OBJ2(ASSETS["pochita"]))
    gpuSombra    = createGPUShape(pipeline, read_OBJ2(ASSETS["nave"]))
    gpuMuro      = np.zeros(muros.total, dtype=object)

    
    gpuSuelo.texture     = textura("pasto_text")
    gpuNave.texture      = textura("red") 
    gpuPilar.texture     = textura("ladrillo_text")
    gpuAmong1.texture    = textura("red")
    gpuAmong2.texture    = textura("blue")
    gpuPochita.texture   = textura("pochita_text")
    gpuSombra.texture    = textura("black")

    for i in range(muros.total):
        gpuMuro[i]         = createGPUShape(pipeline, createTextureNormalsCube(1/4, muros.posiciones[i][2]/4, muros.posiciones[i][2]/4, 1/4))
        gpuMuro[i].texture = textura("ladrillo_text")
#-----------------------------------
    #transformaciones basicas al modelo nave
    navemodelo = SceneGraphNode("navemodelo")    
    navemodelo.transform = tr.matmul([tr.rotationY(np.pi/2), tr.uniformScale(0.08)])
    navemodelo.childs += [gpuNave]

    sombra           = SceneGraphNode("sombra")
    sombra.transform = tr.identity()
    sombra.childs   += [gpuSombra]

    #cada nave tiene su movimiento
    nave = SceneGraphNode("nave")
    nave.transform = tr.identity()
    nave.childs += [navemodelo]

    sombraNave  = SceneGraphNode("sombraNave")
    sombraNave.transform = tr.identity()
    sombraNave.childs    = [sombra]

    nave1 = SceneGraphNode("nave1")
    nave1.transform = tr.identity()
    nave1.childs += [nave]

    sombraNave1 = SceneGraphNode("sombraNave1")
    sombraNave1.transform = tr.identity()
    sombraNave1.childs    = [sombraNave]
#
    #nave2 = SceneGraphNode("nave2")
    #nave2.transform = tr.translate(-1.0,0.0,-0.75)
    #nave2.childs += [nave]
#
    #sombraNave2 = SceneGraphNode("sombraNave2")
    #sombraNave2.transform = tr.translate(-1.0,0.0,-0.75)
    #sombraNave2.childs    = [sombraNave]
#
#
    #nave3 = SceneGraphNode("nave3")
    #nave3.transform = tr.translate(-1.0,0.0,0.75)
    #nave3.childs += [nave]
#
    #sombraNave3 = SceneGraphNode("sombraNave3")
    #sombraNave3.transform = tr.translate(-1.0,0.0,0.75)
    #sombraNave3.childs    = [sombraNave]

    #grupo de naves de mueve en conjunto
    escuadron = SceneGraphNode("escuadron")
    escuadron.transform = tr.identity()
    escuadron.childs += [nave1]
    #escuadron.childs += [nave2]
    #escuadron.childs += [nave3]

    sombraEscuadron  = SceneGraphNode("sombraEscuadron")
    sombraEscuadron.transform = tr.identity()
    sombraEscuadron.childs += [sombraNave1]
    #sombraEscuadron.childs += [sombraNave2]
    #sombraEscuadron.childs += [sombraNave3]
#-----------------------------------
    among1 = SceneGraphNode("among1")
    among1.childs += [gpuAmong1]

    pochita = SceneGraphNode("pochita")
    pochita.childs += [gpuPochita]

    among2 = SceneGraphNode("among2")
    among2.childs += [gpuAmong2]
#-----------------------------------
    textsuelo = SceneGraphNode("textSuelo")
    textsuelo.transform = tr.matmul([tr.translate(0.0,0.0,0.0),
                                     tr.scale(controller.largoMapa+200, 0.01, controller.anchoMapa+30)])
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
                                                      1.0,
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
    escena.childs += [escuadron]
    escena.childs += [suelo]
    escena.childs += [sombraEscuadron]

    return escena
        
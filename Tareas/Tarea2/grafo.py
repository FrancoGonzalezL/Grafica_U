from libs.scene_graph import SceneGraphNode
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from libs.obj_handler import read_OBJ2
from libs.basic_shapes import createTextureNormalsCube

from OpenGL.GL import *
import OpenGL.GL.shaders

import libs.transformations as tr
import numpy as np
import libs.easy_shaders as sh

ASSETS = {
    "nave" :   getAssetPath("nave.obj"),
    "among1" : getAssetPath("Among.obj"),
    "among2":  getAssetPath("Among.obj"),
    "pochita": getAssetPath("pochita3.obj"),

    "pilar1": getAssetPath("Rocas\RockPillars_1.obj"),
    "pilar2": getAssetPath("Rocas\RockPillars_2.obj"),
    "pilar3": getAssetPath("Rocas\RockPillars_3.obj"),
    "pilar4": getAssetPath("Rocas\RockPillars_4.obj"),
    "pilar5": getAssetPath("Rocas\RockPillars_5.obj"),
    "pilar6": getAssetPath("Rocas\RockPillars_6.obj"),
    "pilar7": getAssetPath("Rocas\RockPillars_7.obj"),

    "pochita_text": getAssetPath("pochita.png"),
    "rock":         getAssetPath("ROCK.jpg"),
    "nave_text":     getAssetPath("nave_text.png"),
    "among_text":    getAssetPath("among2.png"),


    "red":         getAssetPath("RED.png"),
    "green":       getAssetPath("GREEN.jpg"),
    "blue":        getAssetPath("BLUE.jpg"),
    "grey":        getAssetPath("GREY.jpg")
}

def textura(text):
    return sh.textureSimpleSetup(ASSETS[text], GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR)

def grafo(controller,pipeline,muros,meteorit):

    gpuPilares = np.array([
                    #createGPUShape(pipeline, read_OBJ2(ASSETS["pilar2"])),
                    #createGPUShape(pipeline, read_OBJ2(ASSETS["pilar3"])),
                    createGPUShape(pipeline, read_OBJ2(ASSETS["pilar4"])),
                    #createGPUShape(pipeline, read_OBJ2(ASSETS["pilar5"])),
                    #createGPUShape(pipeline, read_OBJ2(ASSETS["pilar6"])),
                    ])
    for i in range(len(gpuPilares)):
        gpuPilares[i].texture = textura("rock")
    
    gpuSuelo     = createGPUShape(pipeline, createTextureNormalsCube())
    gpuMeteorito = createGPUShape(pipeline, read_OBJ2(ASSETS["pilar1"]))
    gpuNave      = createGPUShape(pipeline, read_OBJ2(ASSETS["nave"]))
    gpuAmong1    = createGPUShape(pipeline, read_OBJ2(ASSETS["among1"]))
    gpuAmong2    = createGPUShape(pipeline, read_OBJ2(ASSETS["among2"]))
    gpuPochita   = createGPUShape(pipeline, read_OBJ2(ASSETS["pochita"]))

    
    gpuSuelo.texture     = textura("green")
    gpuMeteorito.texture = textura("rock")
    gpuNave.texture      = textura("red") 
    gpuAmong1.texture    = textura("red")
    gpuAmong2.texture    = textura("blue")
    gpuPochita.texture   = textura("pochita_text")
#-----------------------------------
    #transformaciones basicas al modelo nave
    navemodelo = SceneGraphNode("navemodelo")    
    navemodelo.transform = tr.matmul([tr.rotationY(np.pi/2), tr.uniformScale(0.2)])
    navemodelo.childs += [gpuNave]

    #cada nave tiene su movimiento
    nave = SceneGraphNode("nave")
    nave.transform = tr.identity()
    nave.childs += [navemodelo]

    nave1 = SceneGraphNode("nave1")
    nave1.transform = tr.identity()
    nave1.childs += [nave]

    nave2 = SceneGraphNode("nave2")
    nave2.transform = tr.translate(-2.0,0.0,-1.5)
    nave2.childs += [nave]

    nave3 = SceneGraphNode("nave3")
    nave3.transform = tr.translate(-2.0,0.0,1.5)
    nave3.childs += [nave]

    #grupo de naves de mueve en conjunto
    naves = SceneGraphNode("naves")
    naves.transform = tr.identity()
    naves.childs += [nave1]
    naves.childs += [nave2]
    naves.childs += [nave3]
#-----------------------------------
    among1 = SceneGraphNode("among1")
    among1.childs += [gpuAmong1]

    pochita = SceneGraphNode("pochita")
    pochita.childs += [gpuPochita]

    among2 = SceneGraphNode("among2")
    among2.childs += [gpuAmong2]
#-----------------------------------

    textsuelo = SceneGraphNode("textSuelo")
    textsuelo.transform = tr.matmul([tr.translate(0.0,0.0,10.0),
                                     tr.scale(controller.largoMapa+200,1.0,controller.anchoMapa+30)])
    textsuelo.childs += [gpuSuelo]
    suelo = SceneGraphNode("suelo")
    suelo.transform = tr.translate(controller.largoMapa/2, -1.0,0.0)
    suelo.childs += [textsuelo]
    suelo.childs += [pochita]
    suelo.childs += [among1]
    suelo.childs += [among2]

#-----------------------------------
    murosL = np.zeros(len(muros.posiciones),dtype=object)
    for i in range(len(muros.posiciones)):
        murosL[i] = SceneGraphNode("pilar"+str(i))
        murosL[i].transform = tr.matmul([tr.translate(muros.posiciones[i][0]-controller.largoMapa/2,
                                                      2.0,
                                                      muros.posiciones[i][1]-controller.anchoMapa/2),
                                        tr.scale(1.0, muros.posiciones[i][2], muros.posiciones[i][3]),
                                        tr.uniformScale(0.1)])
        murosL[i].childs += [gpuPilares[np.random.randint(0,len(gpuPilares))]]
        suelo.childs += [murosL[i]]

    meteoritos = np.zeros(meteorit.total, dtype=object)
    for i in range(meteorit.total):
        meteoritos[i] = SceneGraphNode("meteorito"+str(i))
        meteoritos[i].childs += [gpuMeteorito]
        suelo.childs += [meteoritos[i]]
#----------------------------------- 

    escena = SceneGraphNode("escena")
    escena.childs += [naves]
    escena.childs += [suelo]

    return escena
        
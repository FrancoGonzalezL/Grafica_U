from libs.scene_graph import SceneGraphNode
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from libs.obj_handler import read_OBJ
from libs.basic_shapes import createColorNormalsCube

import libs.transformations as tr
import numpy as np
import libs.easy_shaders as sh

ASSETS = {
    "nave" : getAssetPath("xwing211.obj"),
    "objeto1" : getAssetPath("crewmate.obj"),
    "pochita": getAssetPath("pochita3.obj"),
    "roca": getAssetPath("crewmate.obj")
}


def grafo(controller,pipeline,muros):

    gpuMuro    = createGPUShape(pipeline, createColorNormalsCube(0.5, 0.5, 0.5))
    gpuSuelo   = createGPUShape(pipeline, createColorNormalsCube(0.0, 0.4, 0.0))
    gpuNave    = createGPUShape(pipeline, read_OBJ(ASSETS["nave"],    (0.8, 0.3, 0.3)))
    gpuAmong   = createGPUShape(pipeline, read_OBJ(ASSETS["objeto1"], (1.0, 0.0, 0.0)))
    gpuPochita = createGPUShape(pipeline, read_OBJ(ASSETS["pochita"], (1.0,1.0,1.0)))
    gpuRoca    = createGPUShape(pipeline, read_OBJ(ASSETS["roca"], (0.3,0.9,0.3)))

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
    among = SceneGraphNode("among")
    among.childs += [gpuAmong]

    pochita = SceneGraphNode("pochita")
    pochita.childs += [gpuPochita]

    roca = SceneGraphNode("roca")
    roca.childs += [gpuRoca]
#-----------------------------------

    textsuelo = SceneGraphNode("textSuelo")
    textsuelo.transform = tr.matmul([tr.translate(0.0,0.0,5.0),
                                     tr.scale(controller.largoMapa,1.0,controller.anchoMapa+10)])
    textsuelo.childs += [gpuSuelo]
    suelo = SceneGraphNode("suelo")
    suelo.transform = tr.translate(controller.largoMapa/2, -1.0,0.0)
    suelo.childs += [textsuelo]

    murosL = np.zeros(len(muros.posiciones),dtype=object)
    for i in range(len(muros.posiciones)):
        murosL[i] = SceneGraphNode("muro"+"i")
        murosL[i].transform = tr.matmul([tr.translate(muros.posiciones[i][0]-controller.largoMapa/2, 2.0 ,muros.posiciones[i][1]-controller.anchoMapa/2),
                                        tr.scale(1.0, muros.posiciones[i][2], muros.posiciones[i][3])])
        murosL[i].childs += [gpuMuro]
        suelo.childs += [murosL[i]]
#----------------------------------- 
    escena = SceneGraphNode("escena")
    escena.childs += [naves]
    escena.childs += [among]
    escena.childs += [suelo]
    escena.childs += [pochita]
    escena.childs += [suelo]
    escena.childs += [roca]

    return escena
        
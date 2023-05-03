from libs.scene_graph import SceneGraphNode
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from libs.obj_handler import read_OBJ
from libs.basic_shapes import createColorNormalsCube

import libs.transformations as tr
import numpy as np
import libs.easy_shaders as sh

ASSETS = {
    "nave" : getAssetPath("nave.obj"),
    "objeto1" : getAssetPath("crewmate.obj"),
    "pochitatxt": getAssetPath("pochita.png")
}

def gpuObjeto(pipeline, modelo, textura, color):
    ex_shape = createGPUShape(pipeline, read_OBJ(ASSETS[modelo],color))
    #tex_params = [GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST]
    #current_tex = ASSETS[textura]
    #ex_shape.texture = sh.textureSimpleSetup(
    #    current_tex, *tex_params
    #)
    return ex_shape


def grafo(pipeline):

    gpuSuelo = createGPUShape(pipeline, createColorNormalsCube(0.0, 0.3, 0.0))
    gpuNave  = gpuObjeto(pipeline, "nave", "pochitatxt", (0.5, 0.5, 0.5))
    gpuAmong = gpuObjeto(pipeline, "objeto1", "pochitatxt",(1, 0.0, 0.0))

    #---------------------------------------------------
    #gpuObjetos = np.zeros(len(ASSETS)-1 ,dtype=object)
    #for i in range(len(gpuObjetos)):
    #    gpuObjetos[i] = createGPUShape(pipeline, read_OBJ(ASSETS["objeto"+str(i+1)], (1,0.0,0.0)))    
    #objetos = np.zeros(len(gpuObjetos), dtype=object)
    #for i in range(len(objetos)):
    #    objetos[i] = SceneGraphNode("objeto"+str(i+1))
    #    objetos[i].transform = tr.identity()
    #    objetos[i].childs += [gpuObjetos[i]]
#-----------------------------------------

    nave1 = SceneGraphNode("nave1")    
    nave1.transform = tr.matmul([tr.rotationY(3*np.pi/2), tr.uniformScale(0.2)])
    nave1.childs += [gpuNave]

    movnave1 = SceneGraphNode("movnave1")
    movnave1.transform = tr.identity()
    movnave1.childs += [nave1]

    naves = SceneGraphNode("naves")
    naves.transform = tr.identity()
    naves.childs += [movnave1]

#-----------------------------------

    among = SceneGraphNode("among")
    among.transform = tr.identity()
    among.childs += [gpuAmong]

#-----------------------------------

    suelo = SceneGraphNode("suelo")
    suelo.transform = tr.matmul([tr.translate(0,-2,0),tr.scale(100,0.1,4)])
    suelo.childs += [gpuSuelo]
    
    escena = SceneGraphNode("escena")
    escena.childs += [naves]
    escena.childs += [among]
    escena.childs += [suelo]
    #for objeto in objetos:
    #    escena.childs += [objeto]

    return escena
        
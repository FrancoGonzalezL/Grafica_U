from libs.scene_graph import SceneGraphNode
from libs.gpu_shape import createGPUShape
from libs.assets_path import getAssetPath
from libs.obj_handler import read_OBJ

import libs.transformations as tr
import numpy as np

ASSETS = {
    "nave" : getAssetPath("nave.obj"),
    "objeto1" : getAssetPath("crewmate.obj")
}

def grafo(pipeline):

    gpuNave = createGPUShape(pipeline, read_OBJ(ASSETS["nave"], (0.0,1.0,1.0)))

    gpuObjetos = np.zeros(len(ASSETS)-1 ,dtype=object)
    for i in range(len(gpuObjetos)):
        gpuObjetos[i] = createGPUShape(pipeline, read_OBJ(ASSETS["objeto"+str(i+1)], (1,0.0,0.0)))    


    objetos = np.zeros(len(gpuObjetos), dtype=object)
    for i in range(len(objetos)):
        objetos[i] = SceneGraphNode("objeto"+str(i+1))
        objetos[i].transform = tr.identity()
        objetos[i].childs += [gpuObjetos[i]]


    nave1 = SceneGraphNode("nave1")    
    nave1.transform = tr.matmul([tr.rotationY(np.pi/2), tr.scale(1.0,1.0,1.0)])
    nave1.childs += [gpuNave]



    nave = SceneGraphNode("naves")
    nave.childs += [nave1]

#-----------------------------------
    escena = SceneGraphNode("escena")
    escena.childs += [nave]
    for objeto in objetos:
        escena.childs += [objeto]

    return escena
        
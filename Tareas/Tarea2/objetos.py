import libs.transformations as tr
import numpy as np
from libs.scene_graph import findNode

class Camera:
    def __init__(self, width , height,):
        self.eye = np.array([-9.0, 9.0, 9.0])
        self.at  = np.array([ 0.0, 0.0, 0.0])
        self.up  = np.array([ 0.0, 1.0, 0.0])

        self.projection = tr.ortho(-9, 9, -9, 9, 0.1, 100)
        self.view = tr.lookAt(self.eye, self.at, self.up)

    def update(self, nave):
        #mirar siempre desde una de las esquinas del cubo
        self.eye = np.array([nave.posx-9, 9.0, 9.0])
        self.at  = np.array([nave.posx,   0.0, 0.0])
        self.view = tr.lookAt(self.eye, self.at, self.up)

class Nave:
    def __init__(self):
        self.speedx = 0
        self.speedz = 0
        self.posx = 0
        self.posz = 0

    def move(self,grafo,dt):
        self.posx += dt*self.speedx
        self.posz += dt*self.speedz
        naves = findNode(grafo,"naves")
        naves.transform = tr.translate(self.posx, 0.0, self.posz)

        movnave = findNode(grafo, "movnave1")
        if self.speedz!=0 and self.speedx!=0:
            movnave.transform = tr.rotationY(np.arctan(-float(self.speedx)/float(self.speedz)))
        elif self.speedz != 0 and self.speedx == 0:
            if self.speedz>0:
                movnave.transform = tr.rotationX(np.pi/4)
            else:
                movnave.transform = tr.rotationX(-np.pi/4)
        else:
            movnave.transform = tr.identity()
        

         


class Obstaculos:
    def __init__(self,nodo,pos,speed):
        self.nodo = nodo
        self.speedrotationX = np.random.random()
        self.speedrotationY = np.random.random()
        self.speedrotationZ = np.random.random()
        self.speed = 4
        self.z = 0

    def move(self,controller,grafo,dt):
        self.z += dt*self.speed
        if np.absolute(self.z)>4:
            self.speed = -self.speed
            
        objeto = findNode(grafo, self.nodo)
        objeto.transform = tr.matmul([tr.translate(5, 0.0, self.z),
                                      tr.rotationX(self.speedrotationX*controller.total_time),
                                      tr.rotationY(self.speedrotationY*controller.total_time),
                                      tr.rotationZ(self.speedrotationZ*controller.total_time),
                                      tr.uniformScale(1.0)])

        
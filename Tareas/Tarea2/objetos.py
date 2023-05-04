import libs.transformations as tr
import numpy as np
from libs.scene_graph import findNode

class Camera:
    def __init__(self,controller, width , height,):
        dim = controller.dim
        self.eye = np.array([-dim, dim, dim])
        self.at  = np.array([ 0.0, 0.0, 0.0])
        self.up  = np.array([ 0.0, 1.0, 0.0])

        self.projection = tr.ortho(-dim, dim, -dim, dim, 0.1, 100)
        self.view = tr.lookAt(self.eye, self.at, self.up)

    def update(self, controller, nave):
        #mirar siempre desde una de las esquinas del cubo
        self.eye = np.array([nave.positionX-controller.dim, controller.dim, controller.dim])
        self.at  = np.array([nave.positionX, 0.0, 0.0])
        self.view = tr.lookAt(self.eye, self.at, self.up)

class Nave:
    def __init__(self):
        self.speedX = 0
        self.speedY = 0
        self.speedZ = 0
        self.positionX = 0
        self.positionY = 0
        self.positionZ = 0

        self.rotationX = 0
        self.rotationY = 0
        self.rotationZ = 0

        self.rot1 = 0
        self.rot2 = 0

    def move(self,controller,grafo,dt):
        self.positionX += dt*self.speedX
        self.positionY += dt*self.speedY
        self.positionZ += dt*self.speedZ

        naves = findNode(grafo,"naves")
        naves.transform = tr.translate(self.positionX, self.positionY, self.positionZ)


        nave = findNode(grafo, "nave")
        nave.transform = tr.matmul([tr.rotationX(np.pi/6*self.rotationX),
                                    tr.rotationY(np.pi/6*self.rotationY),
                                    tr.rotationZ(np.pi/12*self.rotationZ)])

class Obstaculos:
    def __init__(self,controller,nodo,escala):
        self.nodo = nodo
        self.escala = escala
        self.speedZ = np.random.random()*6
        self.positionX = np.random.randint(0,controller.largoMapa)
        self.positionZ = np.random.randint(0,controller.anchoMapa)
        self.positionY = np.random.randint(1, 4)
        self.speedrotationX = np.random.random()*2
        self.speedrotationY = np.random.random()*2
        self.speedrotationZ = np.random.random()*2

    def move(self,controller,grafo,dt):
        self.positionZ += dt*self.speedZ
        if np.absolute(self.positionZ) > controller.anchoMapa/2:
            self.speedZ = -self.speedZ
            
        objeto = findNode(grafo, self.nodo)
        objeto.transform = tr.matmul([tr.translate(self.positionX, self.positionY, self.positionZ),
                                      tr.rotationX(self.speedrotationX*controller.total_time),
                                      tr.rotationY(self.speedrotationY*controller.total_time),
                                      tr.rotationZ(self.speedrotationZ*controller.total_time),
                                      tr.uniformScale(self.escala)])

class MurosMapa:
    def __init__(self,controller):
        self.total = 0
        self.posiciones = []
        for i in range(controller.largoMapa):
            for j in range(controller.anchoMapa):
                if np.random.random() < 0.05 :
                    self.posiciones.append([i,j,int(1 + np.random.random()*3),int(1+np.random.random()*4)])
                    self.total += 1

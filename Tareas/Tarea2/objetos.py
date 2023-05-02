import libs.transformations as tr
import numpy as np
from libs.scene_graph import findNode


class Nave:
    def __init__(self,grafo):
        self.speedx = 0
        self.speedz = 0
        self.posx = 0
        self.posz = 0
        self.grafo = grafo

    def move(self,dt):
        self.posx += dt*self.speedx
        self.posz +=dt*self.speedz

        nave = findNode(self.grafo,"naves")
        nave.transform = tr.translate(self.posx, 0.0, self.posz)
         


class Obstaculos:
    def __init__(self,grafo,pos,speed):
        self.rotation = 0
        self.speedrotation = 0.5
        self.speed = 0
        self.x = 0
        self.y = 0
        self.z = 0

    def move(self,dt):
        self.x += dt*self.speed
        if self.x>13:
            self.x = -13
        self.rotation += dt*self.speedrotation

        objeto = findNode(self.grafo, "objeto"+str(1))
        objeto.transform = tr.matmul([tr.translate(self.x,0.0,self.z),tr.rotationX(self.rotation)])
        
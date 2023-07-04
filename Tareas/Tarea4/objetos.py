import libs.transformations as tr
import numpy as np
from libs.scene_graph import findNode, SceneGraphNode
from libs.basic_shapes import createTextureNormalsCube
from libs.assets_path import getAssetPath
from libs.gpu_shape import createGPUShape
from libs.shaders import textureSimpleSetup
from OpenGL.GL import *
from itertools import chain

import pyglet

class Camera:
    def __init__(self,controller, width , height,):
        dim = controller.dim
        div = controller.div
        self.projections = [
                tr.perspective(60, float(width)/float(height), 0.1, 100),
                tr.ortho(-dim/2, dim/2, -dim/2, dim/2, 0.1, 100),
                tr.perspective(60, float(width)/float(height), 0.1, 100),
                ]
        self.n_project  = 0
        self.projection = self.projections[self.n_project]

        self.eye = np.array([dim/2, 10, dim/2])
        at  = np.array([dim/2, 0.0, dim/2])
        up  = np.array([ 1.0, 0.0, 0.0])
        self.view = tr.lookAt(self.eye, at, up)

    def update(self, controller, boid1:list, speed_boid1:list):
        if self.n_project == 0:
            x,  y,  z  = boid1[0], boid1[1], boid1[2]
            vx, vy, vz = speed_boid1[0],speed_boid1[1],speed_boid1[2]

            theta = np.arctan2(vz, vx)
            phi = np.arctan2(vy, 4)
            nave_pos = [x, y, z, 1]
            eye  = tr.matmul([ tr.translate(nave_pos[0], nave_pos[1], nave_pos[2]),
                               tr.rotationY(-theta),
                               tr.translate(-3.0, 3*np.sin(-phi), 0.0),
                               [0.0, 0.0, 0.0, 1.0]])
            self.eye = np.array(eye[0:3])
            self.view = tr.lookAt(self.eye,
                                  np.array(nave_pos[0:3]),
                                  np.array([0.0,1.0,0.0]))

        elif self.n_project == 1:
            #mirar siempre desde una de las esquinas del cubo
            dim = controller.dim
            self.eye = np.array([dim/2,
                                 dim + 1,
                                 dim/2])
            at  = np.array([dim/2, 0.0, dim/2])
            self.view = tr.lookAt(self.eye, at, np.array([1.0,0.0,0.0]))
        else:
            dim = controller.dim
            self.eye = np.array([-dim, dim/2, dim/2])
            at       = np.array([ dim/2, dim/2, dim/2])
            self.view = tr.lookAt(self.eye, at, np.array([0.0,1.0,0.0]))



def alineamiento(i,pos,speed,R):
    x, y, z = pos[i][0], pos[i][1], pos[i][2]
    ax, ay, az = 0.0, 0.0, 0.0
    total = 0
    for j, p in enumerate(pos):
        if 0.0 < (x-p[0])*(x-p[0]) + (y-p[1])*(y-p[1]) + (z-p[2])*(z-p[2]) < R*R:
            total += 1
            ax += speed[j][0]
            ay += speed[j][1]
            az += speed[j][2]
    if total>0:
        return (ax/total-speed[i][0], ay/total-speed[i][1], az/total-speed[i][2])
    return (0.0,0.0,0.0)

def cohesion(i,pos,R):
    x, y, z = pos[i][0], pos[i][1], pos[i][2]
    ax, ay, az = 0.0, 0.0, 0.0
    total = 0
    for p in pos:
        if 0.0 < (x-p[0])*(x-p[0]) + (y-p[1])*(y-p[1]) + (z-p[2])*(z-p[2]) < R*R:
            total += 1
            ax += p[0]
            ay += p[1]
            az += p[2]
    if total>0:
        return (ax/total-x, ay/total-y, az/total-z)
    return (0.0,0.0,0.0)

def separacion(i,pos,R):
    x, y, z = pos[i][0], pos[i][1], pos[i][2]
    ax, ay, az = 0.0, 0.0, 0.0
    total = 0
    for p in pos:
        if 0.0 < (x-p[0])**2 + (y-p[1])**2 + (z-p[2])**2 < R*R:
            total += 1
            dist = np.sqrt((x-p[0])**2+(y-p[1])**2+(z-p[2])**2)
            ax -= (p[0]-x)/dist
            ay -= (p[1]-y)/dist
            az -= (p[2]-z)/dist
    if total > 0:
        return (ax/total, ay/total, az/total)
    return (0.0,0.0,0.0)

def evasion(i,pos, muros, R):
    x, y, z = pos[i][0], pos[i][1], pos[i][2]
    ax, ay, az = 0.0, 0.0, 0.0
    total = 0
    for p in muros:
        if 0.0 < (x-p[0])*(x-p[0]) + (z-p[1])*(z-p[1]) < R*R:
            total += 1
            dist = ((x-p[0])**2 + (z-p[1])**2)
            ax -= (p[0]-x)/dist
            az -= (p[1]-z)/dist
    if total > 0:
        return (ax/total, ay/total, az/total)
    return (0.0,0.0,0.0)


class Boid:
    def __init__(self, total, dim, max_speed, R1=5, R2=5, R3=5, R4=5,F1=1,F2=1,F3=1,F4=1):
        self.R     = np.array([R1,R2,R3,R4])
        self.F     = np.array([F1,F2,F3,F4])
        self.m_v   = max_speed 
        self.pos   = np.ones((total,3), dtype=float)
        self.speed = np.zeros((total,3),dtype=float)
        for i in range(len(self.pos)):
            self.pos[i][0] = (np.random.random()-0.5)*dim/2 + dim/2
            self.pos[i][1] = (np.random.random())*dim/3 + 0.6
            self.pos[i][2] = (np.random.random()-0.5)*dim/2 + dim/2

            self.speed[i][0] = (np.random.random()-0.5)*2*self.m_v
            self.speed[i][2] = (np.random.random()-0.5)*2*np.sqrt((self.m_v)**2 - (self.speed[i][0])**2)

            p = 1 if np.random.randint(2)==0 else-1
            self.speed[i][1] = np.sqrt((self.m_v)**2 - (self.speed[i][0])**2 - (self.speed[i][2])**2 )*p
        self.data = None
    
    def step(self,controller,muros,grafo,dt):
        pos = self.pos.copy()
        speed = self.speed.copy()

        for i in range(len(pos)):
            ax, ay, az = alineamiento(i,pos,speed,self.R[0])
            bx, by, bz = cohesion(i,pos,self.R[1])
            cx, cy, cz = separacion(i,pos,self.R[2])
            dx, dy, dz = evasion(i,pos,muros,self.R[3])

            self.speed[i][0] += (self.F[0]*ax+self.F[1]*bx+self.F[2]*cx+self.F[3]*dx)*dt
            self.speed[i][1] += (self.F[0]*ay+self.F[1]*by+self.F[2]*cy+self.F[3]*dy)*dt
            self.speed[i][2] += (self.F[0]*az+self.F[1]*bz+self.F[2]*cz+self.F[3]*dz)*dt

            s = np.sqrt((self.speed[i][0])**2 + (self.speed[i][1])**2 + (self.speed[i][2])**2)
            self.speed[i][0] = self.m_v*self.speed[i][0]/s
            self.speed[i][1] = self.m_v*self.speed[i][1]/s
            self.speed[i][2] = self.m_v*self.speed[i][2]/s

            self.pos[i][0] += self.speed[i][0]*dt
            self.pos[i][1] += self.speed[i][1]*dt
            self.pos[i][2] += self.speed[i][2]*dt

            if self.pos[i][0] < 0.0:
                self.pos[i][0] = 0.0
                self.speed[i][0] = -self.speed[i][0]
            elif self.pos[i][0] > controller.dim:
                self.pos[i][0] = controller.dim
                self.speed[i][0] = -self.speed[i][0]
            if self.pos[i][2] < 0.0:
                self.pos[i][2] = 0.0
                self.speed[i][2] = -self.speed[i][2]
            elif self.pos[i][2] > controller.dim:
                self.pos[i][2] = controller.dim
                self.speed[i][2] = -self.speed[i][2]

            if  self.pos[i][1] < 0.5:
                self.pos[i][1] = 0.5
                self.speed[i][1] = -self.speed[i][1]

            elif self.pos[i][1] > controller.dim:            
                 self.pos[i][1] = controller.dim
                 self.speed[i][1] = -self.speed[i][1]

            theta = np.arctan2(self.speed[i][2], self.speed[i][0])
            phi =   np.arctan2(self.speed[i][1], 4)

            nave = findNode(grafo, "nave"+str(i))
            nave.transform = tr.matmul([
                                        tr.translate(self.pos[i][0], self.pos[i][1], self.pos[i][2]),
                                        tr.rotationY(-theta),
                                        tr.rotationZ(phi)
                                        ])


#Este Grupo solo da vueltas
class Obstaculos:
    def __init__(self,controller,nodo,escala):
        self.nodo   = nodo
        self.escala = escala
        self.speedZ = np.random.random()*6
        self.positionX = np.random.random()*controller.dim
        self.positionZ = np.random.random()*controller.dim
        self.positionY = np.random.randint(2, 4)
        self.speedrotationX = np.random.random()*2
        self.speedrotationY = np.random.random()*2
        self.speedrotationZ = np.random.random()*2

    def update(self,controller,grafo,dt):

        self.positionZ += dt*self.speedZ
        if self.positionZ > controller.dim/2 and self.speedZ > 0:
            self.speedZ = -self.speedZ
        elif self.positionZ < -controller.dim/2 and self.speedZ < 0:
            self.speedZ = -self.speedZ
            
        objeto = findNode(grafo, self.nodo)
        objeto.transform = tr.matmul([tr.translate(self.positionX, self.positionY, self.positionZ),
                                      tr.rotationX(self.speedrotationX*controller.total_time),
                                      tr.rotationY(self.speedrotationY*controller.total_time),
                                      tr.rotationZ(self.speedrotationZ*controller.total_time),
                                      tr.uniformScale(self.escala)])

#grupo con posiciones aleatorias pero estaticas
class MurosMapa:
    def __init__(self,controller,densidad):
        self.total = 0
        posiciones = []
        for i in range(controller.dim):
            for j in range(controller.dim):
                if np.random.random() < densidad:
                    posiciones.append([i, j, controller.dim])
                    self.total += 1
        self.posiciones = np.array(posiciones)

#Grupo con todo aleatorio
class Meteoritos:
    def __init__(self,controller,nodo,total):
        self.nodo = nodo
        self.total = total
        self.meteoritos = np.zeros((total,9),dtype=float)
        for i in range(total):
            self.meteoritos[i][0] = (0.5-np.random.random())*controller.dim #X
            self.meteoritos[i][1] = np.random.randint(80,120)                      #Y
            self.meteoritos[i][2] = (0.5-np.random.random())*controller.dim #Z

            self.meteoritos[i][3] = (0.5-np.random.random())*10    #SpeedX
            self.meteoritos[i][4] = -10 -np.random.random()* 10    #SpeedY
            self.meteoritos[i][5] = (0.5-np.random.random())*10    #SpeedZ

            self.meteoritos[i][6] = np.random.random()*np.pi #angular_speedX
            self.meteoritos[i][7] = np.random.random()*np.pi #Y
            self.meteoritos[i][8] = np.random.random()*np.pi #Z
    
    def update(self,controller,grafo,dt):
        g = -9.8
        for i in range(self.total):    
            self.meteoritos[i][0] += dt*self.meteoritos[i][3]
            self.meteoritos[i][2] += dt*self.meteoritos[i][5]

            if abs(self.meteoritos[i][4]) < 0.01 and abs(self.meteoritos[i][1] - 1) < 0.01: 
                self.meteoritos[i][0]  = (0.5-np.random.random())*controller.dim
                self.meteoritos[i][1]  = np.random.randint(50,120)
                self.meteoritos[i][2]  = (0.5-np.random.random())*controller.dim
                self.meteoritos[i][4]  = -10 -np.random.random()*10
                
            elif self.meteoritos[i][1] + dt*(self.meteoritos[i][4] + dt*g*0.5) > 1:                 
                self.meteoritos[i][1] += dt*(self.meteoritos[i][4] + dt*g*0.5)
                self.meteoritos[i][4] += dt*g
            else:
                speed_ = (self.meteoritos[i][4]**2 + 2*abs(g)*abs(self.meteoritos[i][1] - 1))**0.5
                dt1 = (speed_ - abs(self.meteoritos[i][4])) / abs(g)
                self.meteoritos[i][1] += dt1*(self.meteoritos[i][4] + dt1*g*0.5)
                self.meteoritos[i][4]  = abs(self.meteoritos[i][4] + dt1*g)*0.4
                self.meteoritos[i][1] += (dt-dt1)*(self.meteoritos[i][4]+(dt-dt1)*g*0.5)
                self.meteoritos[i][4] += (dt-dt1)*g


            meteoritoG = findNode(grafo, self.nodo+str(i))
            meteoritoG.transform = tr.matmul([tr.translate(self.meteoritos[i][0], self.meteoritos[i][1], self.meteoritos[i][2]),
                                              tr.rotationX(self.meteoritos[i][6]*controller.total_time),
                                              tr.rotationY(self.meteoritos[i][7]*controller.total_time),
                                              tr.rotationZ(self.meteoritos[i][8]*controller.total_time),
                                              tr.scale(1.0,0.5,1.0)])

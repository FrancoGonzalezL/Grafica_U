import libs.transformations as tr
import numpy as np
from libs.scene_graph import findNode
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
                tr.ortho(-dim/2, dim/2, -dim/2, dim/2, 0.1, 100)
                ]
        self.n_project  = 1
        self.projection = self.projections[self.n_project]

        self.eye = np.array([dim/2, 10, dim/2])
        at  = np.array([dim/2, 0.0, dim/2])
        up  = np.array([ 1.0, 0.0, 0.0])
        self.view = tr.lookAt(self.eye, at, up)

    def update(self, controller, nave):
        if self.n_project == 0:
            nave_pos = [nave.positionX,nave.positionY,nave.positionZ,1]

            eye  = tr.matmul([ tr.translate(nave_pos[0],nave_pos[1],nave_pos[2]),
                               tr.rotationY(-nave.theta),
                               tr.translate(-5.0,2-5*np.sin(nave.phi),0.0),
                               [0.0,0.0,0.0,1.0]])
            self.eye = np.array(eye[0:3])

            up = tr.matmul([tr.rotationZ(nave.phi),
                            [0.0,1.0,0.0,1.0]])

            self.view = tr.lookAt(self.eye,
                                  np.array(nave_pos[0:3]),
                                  np.array([0.0,1.0,0.0]))

        else:
            #mirar siempre desde una de las esquinas del cubo
            dim = controller.dim
            self.eye = np.array([dim/2,
                                 10,
                                 dim/2])
            at  = np.array([dim/2, 0.0, dim/2])
            self.view = tr.lookAt(self.eye, at, np.array([1.0,0.0,0.0]))


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
    ax, az = 0.0, 0.0
    total = 0
    for p in pos:
        if 0.0 < (x-p[0])*(x-p[0]) + (z-p[2])*(z-p[2]) < R*R:
            total += 1
            dist = np.sqrt((x-p[0])**2+(z-p[2])**2)
            #div por 0
            ax -= 3*(p[0]-x)/dist
            az -= 3*(p[2]-z)/dist
    if total > 0:
        return (ax/total,0.0, az/total)
    return (0.0,0.0,0.0)

def evasion(i,pos, muros, R):
    x, y, z = pos[i][0], pos[i][1], pos[i][2]
    ax, az = 0.0, 0.0
    total = 0
    for p in muros:
        if 0.0 < (x-p[0])*(x-p[0]) + (z-p[1])*(z-p[1]) < R*R:
            total += 1
            dist = ((x-p[0])**2 + (z-p[1])**2)
            #div por 0
            ax -= 20*(p[0]-x)/dist
            az -= 20*(p[1]-z)/dist
    if total > 0:
        return (ax/total, 0.0, az/total)
    return (0.0,0.0,0.0)

class Boid:
    def __init__(self,total,ancho,largo):
        self.pos   = np.ones((total,3), dtype=float)
        self.speed = np.zeros((total,3),dtype=float)
        for i in range(len(self.pos)):
            self.pos[i][0] = (np.random.random()-0.5)*ancho/2 + ancho/2
            self.pos[i][2] = (np.random.random()-0.5)*largo/2 + largo/2

            self.speed[i][0] = (np.random.random()-0.5)*8
            p = 1 if np.random.randint(2)==0 else -1
            self.speed[i][2] = np.sqrt(16-self.speed[i][0]*self.speed[i][0]) *p
        self.data = None
    
    def step(self,controller,muros,dt):
        pos = self.pos.copy()
        speed = self.speed.copy()

        for i in range(len(pos)):
            ax, ay, az = alineamiento(i,pos,speed,5)
            bx, by, bz = cohesion(i,pos,5)
            cx, cy, cz = separacion(i,pos,2)
            dx, dy, dz = evasion(i,pos,muros,2*np.sqrt(2))

            self.speed[i][0] += (ax+bx+cx+dx)*dt
            self.speed[i][2] += (az+bz+cz+dz)*dt

            s = np.sqrt(self.speed[i][0]*self.speed[i][0] + self.speed[i][2]*self.speed[i][2])
            self.speed[i][0] = 4*self.speed[i][0]/s
            self.speed[i][2] = 4*self.speed[i][2]/s

            self.pos[i][0] += self.speed[i][0]*dt
            self.pos[i][2] += self.speed[i][2]*dt

            if self.pos[i][0] < 0.0:
                self.pos[i][0] = controller.dim
            elif self.pos[i][0] > controller.dim:
                self.pos[i][0] = 0.0
            if self.pos[i][2] < 0.0:
                self.pos[i][2] = controller.dim
            elif self.pos[i][2] > controller.dim:
                self.pos[i][2] = 0.0

    def draw(self, pipeline):

        self.data = pipeline.vertex_list(
            len(self.pos), pyglet.gl.GL_POINTS, position="f"
            )
        self.data.position[:] = tuple(
            chain(*((p[0],p[1],p[2]) for p in self.pos))
            )

        glEnable(GL_PROGRAM_POINT_SIZE)

        pipeline.use()
        if self.data is not None:
            self.data.draw(pyglet.gl.GL_POINTS)
        if self.data is not None:
            self.data.delete()
            self.data = None

class Nave:
    def __init__(self,max_speed,max_angular_speed):
        self.positionX = 0
        self.positionZ = 0
        self.positionY = 0
        self.speed     = 0

        self.theta         = 0
        self.angular_speed = 0
        self.phi           = 0

        self.max_speed = max_speed
        self.max_angular_speed = max_angular_speed

    def update(self,grafo,dt=0):
        speed = self.speed*self.max_speed
        angular_speed = self.angular_speed*self.max_angular_speed
        self.theta += dt*angular_speed*np.pi/8

        self.positionX += dt*speed*np.cos(self.theta)*np.cos(self.phi)
        self.positionY += dt*speed*np.sin(self.phi)
        self.positionZ += dt*speed*np.sin(self.theta)*np.cos(self.phi)
        self.positionY = max(0.5, self.positionY)

        naves = findNode(grafo,"escuadron")
        naves.transform = tr.translate(self.positionX,
                                       self.positionY,
                                       self.positionZ)

        nave = findNode(grafo, "nave")
        nave.transform = tr.matmul([tr.rotationY(-self.theta),
                                    tr.rotationZ(self.phi)])

        sombraEscuadron = findNode(grafo, "sombraEscuadron")
        sombraEscuadron.transform = tr.matmul([tr.translate(self.positionX, 0.001, self.positionZ)])

        sombra = findNode(grafo,"sombra")
        sombra.transform = tr.matmul([tr.scale(1.0, 0.001, 1.0),
                                      tr.rotationY(-self.theta),
                                      tr.rotationZ(self.phi),
                                      tr.rotationY(np.pi/2), tr.uniformScale(0.08)])


#Este Grupo solo da vueltas
class Obstaculos:
    def __init__(self,controller,nodo,escala):
        self.nodo   = nodo
        self.escala = escala
        self.speedZ = np.random.random()*6
        self.positionX = np.random.randint(-controller.largoMapa/2,controller.largoMapa/2)
        self.positionZ = np.random.randint(-controller.anchoMapa/2,controller.anchoMapa/2)
        self.positionY = np.random.randint(2, 4)
        self.speedrotationX = np.random.random()*2
        self.speedrotationY = np.random.random()*2
        self.speedrotationZ = np.random.random()*2

    def update(self,controller,grafo,dt):

        self.positionZ += dt*self.speedZ
        if self.positionZ > controller.anchoMapa/2 and self.speedZ > 0:
            self.speedZ = -self.speedZ
        elif self.positionZ < -controller.anchoMapa/2 and self.speedZ < 0:
            self.speedZ = -self.speedZ
            
        objeto = findNode(grafo, self.nodo)
        objeto.transform = tr.matmul([tr.translate(self.positionX, self.positionY, self.positionZ),
                                      tr.rotationX(self.speedrotationX*controller.total_time),
                                      tr.rotationY(self.speedrotationY*controller.total_time),
                                      tr.rotationZ(self.speedrotationZ*controller.total_time),
                                      tr.uniformScale(self.escala)])

#grupo con posiciones aleatorias pero estaticas
class MurosMapa:
    def __init__(self,controller,densidad,altura_max):
        self.total = 0
        posiciones = []
        for i in range(controller.largoMapa):
            for j in range(controller.anchoMapa):
                if np.random.random() < densidad:
                    posiciones.append([i, j, int(1 + np.random.random()*altura_max)])
                    self.total += 1
        self.posiciones = np.array(posiciones)
    def colision(self, x, y, z):
        for muro in self.posiciones:
            mx = muro[0]
            my = muro[2]
            mz = muro[1]
            if abs(x - mx) <= 0.5 and y<=my and abs(z - mz) <= 0.5:
                print("colision")


#Grupo con todo aleatorio
class Meteoritos:
    def __init__(self,controller,nodo,total):
        self.nodo = nodo
        self.total = total
        self.meteoritos = np.zeros((total,9),dtype=float)
        for i in range(total):
            self.meteoritos[i][0] = (0.5-np.random.random())*controller.largoMapa #X
            self.meteoritos[i][1] = np.random.randint(80,120)                      #Y
            self.meteoritos[i][2] = (0.5-np.random.random())*controller.anchoMapa #Z

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
                self.meteoritos[i][0]  = (0.5-np.random.random())*controller.largoMapa
                self.meteoritos[i][1]  = np.random.randint(50,120)
                self.meteoritos[i][2]  = (0.5-np.random.random())*controller.anchoMapa
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

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

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T
def hermiteMatrix(P1, P2, T1, T2):
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])
    return np.matmul(G, Mh)
def bezierMatrix(P0, P1, P2, P3):
    G = np.concatenate((P0, P1, P2, P3), axis=1)
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    return np.matmul(G, Mb)
def evalCurve(M, N):
    ts = np.linspace(0.0, 1.0, N)
    curve = np.ndarray(shape=(N, 3), dtype=float)
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
    return curve



class Camera:
    def __init__(self,controller, width , height,):
        dim = controller.dim
        div = controller.div
        self.projections = [
                tr.perspective(60, float(width)/float(height), 0.1, 100),
                tr.ortho(-dim*div, dim*div, -dim, dim, 0.1, 100)
                ]
        self.n_project  = 1
        self.projection = self.projections[self.n_project]

        self.eye = np.array([-dim, dim, dim])
        at  = np.array([ 0.0, 0.0, 0.0])
        up  = np.array([ 0.0, 1.0, 0.0])
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
            self.eye = np.array([nave.positionX - controller.dim,
                                nave.positionY + controller.dim,
                                nave.positionZ + controller.dim])
            at  = np.array([nave.positionX,nave.positionY,nave.positionZ])
            self.view = tr.lookAt(self.eye, at, np.array([0.0,1.0,0.0]))

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

        naves = findNode(grafo,"escuadron")
        naves.transform = tr.translate(self.positionX,
                                       self.positionY,
                                       self.positionZ)

        nave = findNode(grafo, "nave")
        nave.transform = tr.matmul([tr.rotationY(-self.theta),
                                    tr.rotationZ(self.phi)])

        sombraEscuadron = findNode(grafo, "sombraEscuadron")
        sombraEscuadron.transform = tr.matmul([tr.translate(self.positionX, -0.4, self.positionZ)])

        sombra = findNode(grafo,"sombra")
        sombra.transform = tr.matmul([tr.scale(1.0, 0.01, 1.0),
                                      tr.rotationY(-self.theta),
                                      tr.rotationZ(self.phi),
                                      tr.rotationY(np.pi/2), tr.uniformScale(0.2)])

class Ruta:
    def __init__(self):
        self.ruta = []
        self.tiempo = []
        self.dir = []
        self.ruta_data = None

        self.lines = True

        #self.cubo = createGPUShape(pipeline, createTextureNormalsCube(1,1,1,1))
        #self.cubo.texture = textureSimpleSetup(getAssetPath("RED.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        #self.cubo2 = createGPUShape(pipeline, createTextureNormalsCube(1,1,1,1))
        #self.cubo2.texture = textureSimpleSetup(getAssetPath("BLUE.jpg"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

        self.dibujar = False
        self.reprod  = False
        self.N       = 0
        self.HermiteCurve = np.zeros((0,3))
    
        self.a = []

    def grabar(self,nave,time):
        self.ruta.append([nave.positionX,nave.positionY,nave.positionZ])
        self.tiempo.append(time)
        self.dir.append([nave.theta,nave.phi])
        self.estado()
        
        if len(self.ruta) > 1:
            ref = 60
            #posiciones
            P1 = np.array([[self.ruta[-2][0], self.ruta[-2][1], self.ruta[-2][2]]]).T
            P2 = np.array([[self.ruta[-1][0], self.ruta[-1][1], self.ruta[-1][2]]]).T
            tan = nave.speed*np.sqrt(np.square(self.ruta[-1][0]-self.ruta[-2][0])+np.square(self.ruta[-1][1]-self.ruta[-2][1])+np.square(self.ruta[-1][2]-self.ruta[-2][2]))
            T1 = np.array([[tan*np.cos(self.dir[-2][0])*np.cos(self.dir[-2][1]),
                            tan*np.sin(self.dir[-2][1]),
                            tan*np.sin(self.dir[-2][0])*np.cos(self.dir[-2][1])]]).T
            T2 = np.array([[tan*np.cos(self.dir[-1][0])*np.cos(self.dir[-1][1]),
                            tan*np.sin(self.dir[-1][1]),
                            tan*np.sin(self.dir[-1][0])*np.cos(self.dir[-1][1])]]).T
            GMh = hermiteMatrix(P1, P2, T1, T2)
            HermiteCurve = evalCurve(GMh, int(ref*(self.tiempo[-1]-self.tiempo[-2])))
            self.HermiteCurve = np.concatenate((self.HermiteCurve,HermiteCurve),axis=0)

            self.a.append(len(self.HermiteCurve)-1)

    def reproducir(self,nave,grafo):
        if self.reprod and len(self.HermiteCurve)>0:
            if self.N > len(self.HermiteCurve)-2: self.N = 0
            nave.positionX = self.HermiteCurve[self.N][0]
            nave.positionY = self.HermiteCurve[self.N][1]
            nave.positionZ = self.HermiteCurve[self.N][2]

            if self.N in self.a:#evita errores entre las curvas
                a = np.arctan2(self.HermiteCurve[self.N+2][2] - self.HermiteCurve[self.N+1][2],
                              self.HermiteCurve[self.N+2][0] - self.HermiteCurve[self.N+1][0]) 
                b = np.arctan2(self.HermiteCurve[self.N][2] - self.HermiteCurve[self.N-1][2],
                              self.HermiteCurve[self.N][0] - self.HermiteCurve[self.N-1][0])
                nave.theta = (a+b)*0.5

                dist = np.sqrt((self.HermiteCurve[self.N+2][0]-self.HermiteCurve[self.N+1][0])**2 + \
                            (self.HermiteCurve[self.N+2][2]-self.HermiteCurve[self.N+1][2])**2)
                a = np.arctan2(self.HermiteCurve[self.N+2][1] - self.HermiteCurve[self.N+1][1],dist)
                dist = np.sqrt((self.HermiteCurve[self.N][0]-self.HermiteCurve[self.N-1][0])**2 + \
                            (self.HermiteCurve[self.N][2]-self.HermiteCurve[self.N-1][2])**2)
                b = np.arctan2(self.HermiteCurve[self.N][1] - self.HermiteCurve[self.N-1][1],dist)
                nave.phi = (a+b)*0.5
            else:
                nave.theta = np.arctan2(self.HermiteCurve[self.N+1][2] - self.HermiteCurve[self.N][2],
                                        self.HermiteCurve[self.N+1][0] - self.HermiteCurve[self.N][0])

                dist = np.sqrt((self.HermiteCurve[self.N+1][0]-self.HermiteCurve[self.N][0])**2 + \
                            (self.HermiteCurve[self.N+1][2]-self.HermiteCurve[self.N][2])**2)
                nave.phi = np.arctan2(self.HermiteCurve[self.N+1][1] - self.HermiteCurve[self.N][1],dist)
            
            #Aun hay problemas con el movimiento ):

            nave.update(grafo)
            self.N+=1

    def estado(self):
        if len(self.ruta)!=0:
            print("punto agregado: ",self.ruta[-1],end=", ")
            print("orientacion:", self.dir[-1],end=", ")
            print("total de puntos: ", len(self.ruta))

    def draw(self,pipeline):
        if self.dibujar:

            if self.lines and len(self.HermiteCurve) > 1:

                self.ruta_data = pipeline.vertex_list_indexed(
                len(self.HermiteCurve),
                pyglet.gl.GL_LINES,
                tuple(chain(*([i,i+1] for i in range(len(self.HermiteCurve)-1)))),
                position="f",
                )
                self.ruta_data.position[:] = tuple(
                    chain(*((self.HermiteCurve[i][0], self.HermiteCurve[i][1], self.HermiteCurve[i][2]) for i in range(len(self.HermiteCurve))))
                    )
                modo = pyglet.gl.GL_LINES


            elif not self.lines and len(self.ruta) > 0:
                self.ruta_data = pipeline.vertex_list(
                    len(self.ruta), pyglet.gl.GL_POINTS, position="f"
                    )
                self.ruta_data.position[:] = tuple(
                    chain(*((p[0],p[1],p[2]) for p in self.ruta))
                    )
                modo = pyglet.gl.GL_POINTS
                glEnable(GL_PROGRAM_POINT_SIZE)

            pipeline.use()
            if self.ruta_data is not None:
                self.ruta_data.draw(modo)

            if self.ruta_data is not None:
                self.ruta_data.delete()
                self.ruta_data = None

            #for posicion in self.ruta:
            #    model = tr.matmul([tr.translate(posicion[0],posicion[1],posicion[2]),
            #                    tr.uniformScale(0.2)])
            #    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, model)
            #    pipeline.drawCall(self.cubo)

            #for i,pos in enumerate(self.HermiteCurve):
            #    if i%2==0:
            #        model = tr.matmul([tr.translate(pos[0],pos[1],pos[2]),
            #                        tr.uniformScale(0.05)])
            #        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "model"), 1, GL_TRUE, model)
            #        pipeline.drawCall(self.cubo2)

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
    def __init__(self,controller,densidad,altura_max,largo_max):
        self.total = 0
        posiciones = []
        for i in range(controller.largoMapa):
            for j in range(controller.anchoMapa):
                if np.random.random() < densidad:
                    posiciones.append([i, j, int(1 + np.random.random()*altura_max), int(1+np.random.random()*largo_max)])
                    self.total += 1
        self.posiciones = np.array(posiciones)


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

            if abs(self.meteoritos[i][4]) < 0.01 and abs(self.meteoritos[i][1]) < 0.01: 
                self.meteoritos[i][0]  = (0.5-np.random.random())*controller.largoMapa
                self.meteoritos[i][1]  = np.random.randint(50,120)
                self.meteoritos[i][2]  = (0.5-np.random.random())*controller.anchoMapa
                self.meteoritos[i][4]  = -10 -np.random.random()*10
                
            elif self.meteoritos[i][1] + dt*(self.meteoritos[i][4] + dt*g*0.5) > 0:                 
                self.meteoritos[i][1] += dt*(self.meteoritos[i][4] + dt*g*0.5)
                self.meteoritos[i][4] += dt*g
            else:
                speed_ = (self.meteoritos[i][4]**2 + 2*abs(g)*abs(self.meteoritos[i][1]))**0.5
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

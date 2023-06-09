#Franco González

import sys
import os
import pyglet
import grafo
import objetos

import numpy as np
import libs.shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg

from OpenGL.GL import *
from pathlib import Path
from pyglet.graphics.shader import Shader, ShaderProgram

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

"""
    W,D: para avanzar o retroceder
    A,D: para girar (izquierda, derecha)
    mouse: la nave sube o baja dependiendo de la posicion del mouse
"""

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Tarea3, Franco González"):
        super().__init__(width, height, title)
        self.total_time = 0.0
 
        self.pipeline = sh.SimpleTextureGouraudShaderProgram()
        
        #pipeline para los puntos
        with open(Path(os.path.dirname(__file__)) / "libs/point_vertex_program.glsl") as f:
            vertex_program = f.read()
        with open(Path(os.path.dirname(__file__)) / "libs/point_fragment_program.glsl") as f:
            fragment_program = f.read()
        vert_shader = Shader(vertex_program, "vertex")
        frag_shader = Shader(fragment_program, "fragment")
        self.pipeline2 = ShaderProgram(vert_shader, frag_shader)

        #se puede modificar
        #------------------------
        #self.dim cambia la distancia a la camara y el tamaño de los objetos
        #mientras mas grande su valor mas pequeño se ve todo
        self.dim    = 12
        self.div    = width/height

        #mapa
        self.anchoMapa = 16
        self.largoMapa = 30
        #nave
        self.nave_speed         = 3.3
        self.nave_angular_speed = 3.3
        #OBJETOS
        #muros
        self.muros_densidad   = 0.09
        self.muros_altura_max = 12
        self.muros_largo_max  = 3
        #meteoritos
        self.meteoritos_total = 3
        #------------------------

if __name__ == '__main__':

    WIDTH, HEIGHT = 1000, 700
    controller = Controller(width=WIDTH, height=HEIGHT)
    camera = objetos.Camera(controller, WIDTH, HEIGHT)

    controller.pipeline2.use()


    nave = objetos.Nave(controller.nave_speed, controller.nave_angular_speed)
    ruta = objetos.Ruta()
    muros = objetos.MurosMapa(controller, controller.muros_densidad, controller.muros_altura_max, controller.muros_largo_max)
    meteoritos = objetos.Meteoritos(controller, "meteorito", controller.meteoritos_total)
    obstaculos = np.array([objetos.Obstaculos(controller,"among1", 0.5),
                        objetos.Obstaculos(controller,"pochita", 2.0),
                        objetos.Obstaculos(controller,"among2", 0.6)])
    escena = grafo.grafo(controller,controller.pipeline, muros, meteoritos)


    glUseProgram(controller.pipeline.shaderProgram)
    glClearColor(0.0, 0.7, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ka"), 0.35, 0.35, 0.35)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "constantAttenuation"), 0.0001)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "linearAttenuation"), 0.03)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "quadraticAttenuation"), 0.01)
    glUniform1ui(glGetUniformLocation(controller.pipeline.shaderProgram, "shininess"), 100)


    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            controller.close()

        if symbol == pyglet.window.key.L:
            ruta.lines = not ruta.lines
        if symbol == pyglet.window.key.C:
            camera.n_project = (camera.n_project+1)%2
            camera.projection = camera.projections[camera.n_project]
        if symbol == pyglet.window.key.V:
            ruta.dibujar = not ruta.dibujar
        if symbol == pyglet.window.key._1:
            ruta.N = 0
            ruta.reprod = not ruta.reprod
            
        if ruta.reprod: return
        if symbol == pyglet.window.key.R:
            ruta.grabar(nave)
        elif symbol == pyglet.window.key.W:
            nave.speed =  1
        elif symbol == pyglet.window.key.S:
            nave.speed = -1
        elif symbol == pyglet.window.key.A:
            nave.angular_speed = -1
        elif symbol == pyglet.window.key.D:
            nave.angular_speed =  1
        

    @controller.event
    def on_key_release(symbol, modifiers):
        if ruta.reprod: return
        elif   symbol == pyglet.window.key.W:
            nave.speed = 0
        elif symbol == pyglet.window.key.S:
            nave.speed = 0
        elif symbol == pyglet.window.key.A:
            nave.angular_speed = 0
        elif symbol == pyglet.window.key.D:
            nave.angular_speed = 0

    @controller.event
    def on_mouse_motion(x, y, dx, dy): 
        if ruta.reprod: return
        nave.phi = (y/HEIGHT-1)*np.pi/2 + (y/HEIGHT)*np.pi/2


    @controller.event
    def on_draw():
        controller.clear()
        glUseProgram(controller.pipeline.shaderProgram)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #reproduce la trayectoria grabada
        ruta.reproducir(nave,escena)

        #actualiza camara con la posicion de la nave
        camera.update(controller, nave)
        

        glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "lightPosition"), nave.positionX, nave.positionY + 20, nave.positionZ)
        glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "viewPosition"),  camera.eye[0], camera.eye[1], camera.eye[2])
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, camera.view)

        sg.drawSceneGraphNode(escena, controller.pipeline, "model")

        #dibujo de la curva
        controller.pipeline2["projection"] = camera.projection.reshape(16, 1, order="F")
        controller.pipeline2["view"] = camera.view.reshape(16, 1, order="F")
        
        ruta.draw(controller.pipeline2)


    def update(dt,controller, nave, obstaculos, meteoritos, escena):
        controller.total_time += dt
        nave.update(escena, dt)
        meteoritos.update(controller,escena,dt)
        for obstaculo in obstaculos:
            obstaculo.update(controller,escena, dt)

    pyglet.clock.schedule(update, controller, nave, obstaculos,meteoritos, escena)
    pyglet.app.run(1/60)
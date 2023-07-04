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


class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Tarea4, Franco González"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleTexturePhongShaderProgram()
        #------------------------
        #self.dim cambia la distancia a la camara y el tamaño de los objetos
        #mientras mas grande su valor mas pequeño se ve todo
        self.dim    =  40
        self.div    = width/height

        #OBJETOS
        #muros
        self.muros_densidad   = 0.005
        #meteoritos
        self.meteoritos_total = 5
        #------------------------
        self.total_boids = 75
        self.boid        = 0

if __name__ == '__main__':

    WIDTH, HEIGHT = 1000,1000
    controller = Controller(width=WIDTH, height=HEIGHT)
    camera = objetos.Camera(controller, WIDTH, HEIGHT)
    muros = objetos.MurosMapa(controller, controller.muros_densidad)
    meteoritos = objetos.Meteoritos(controller, "meteorito", controller.meteoritos_total)
    escena = grafo.grafo(controller, controller.pipeline, muros, meteoritos)

    obstaculos = np.array([objetos.Obstaculos(controller,"among1", 0.5),
                        objetos.Obstaculos(controller,"pochita", 2.0),
                        objetos.Obstaculos(controller,"among2", 0.6)])
    
    boid = objetos.Boid(controller.total_boids, controller.dim, 5,
                        5, 5, 3, np.sqrt(2), 1, 1, 3, 15)


    glUseProgram(controller.pipeline.shaderProgram)
    glClearColor(0.0, 0.7, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ka"), 0.5, 0.5, 0.5)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "constantAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "linearAttenuation"), 0.03)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "quadraticAttenuation"), 0.01)
    glUniform1ui(glGetUniformLocation(controller.pipeline.shaderProgram, "shininess"), 100)


    @controller.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            controller.close()

        if symbol == pyglet.window.key.C:
            camera.n_project = (camera.n_project+1)%3
            camera.projection = camera.projections[camera.n_project]
        if symbol == pyglet.window.key.F:
            controller.boid = (controller.boid+1)%controller.total_boids

    @controller.event
    def on_key_release(symbol, modifiers):
        return


    @controller.event
    def on_draw():
        controller.clear()
        glUseProgram(controller.pipeline.shaderProgram)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        camera.update(controller, boid.pos[controller.boid], boid.speed[controller.boid])
        

        glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "lightPosition"), controller.dim/2, controller.dim+10, controller.dim/2)
        glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "viewPosition"),  camera.eye[0], camera.eye[1], camera.eye[2])
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
        glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, camera.view)

        sg.drawSceneGraphNode(escena, controller.pipeline, "model")

    def update(dt,controller, obstaculos, meteoritos, escena, boid,muros):
        boid.step(controller, muros.posiciones, escena, dt)
        controller.total_time += dt
        meteoritos.update(controller,escena,dt)
        for obstaculo in obstaculos:
            obstaculo.update(controller, escena, dt)

    pyglet.clock.schedule(update, controller, obstaculos,meteoritos, escena, boid, muros)
    pyglet.app.run(1/60)
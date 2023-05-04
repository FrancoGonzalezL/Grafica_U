import sys
import os
import pyglet
import grafo
import objetos

import numpy as np
import libs.lighting_shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ, read_OBJ2
from libs.assets_path import getAssetPath
from libs.shapes import createTextureCube
from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 900, 900

class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"tarea2"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleGouraudShaderProgram()
        self.dim = 9
        self.anchoMapa = 15
        self.largoMapa = 30

controller = Controller(width=WIDTH, height=HEIGHT)

nave = objetos.Nave()
muros = objetos.MurosMapa(controller)
escena = grafo.grafo(controller,controller.pipeline, muros)
camera = objetos.Camera(controller, WIDTH, HEIGHT)

obstaculos = np.array([objetos.Obstaculos(controller,"among", 0.5),
                       objetos.Obstaculos(controller,"pochita", 2.0),
                       objetos.Obstaculos(controller,"roca", 0.6)])

glUseProgram(controller.pipeline.shaderProgram)
glClearColor(0.0, 0.7, 1.0, 1.0)
glEnable(GL_DEPTH_TEST)

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()
    elif symbol == pyglet.window.key.W:
        nave.speedX = 2
    elif symbol == pyglet.window.key.S:
        nave.speedX = -2
    elif symbol == pyglet.window.key.A:
        nave.speedZ = -2
        nave.rotationY = 1
    elif symbol == pyglet.window.key.D:
        nave.speedZ = 2
        nave.rotationY =  -1

@controller.event
def on_key_release(symbol, modifiers):
    if   symbol == pyglet.window.key.W:
        nave.speedX = 0
    elif symbol == pyglet.window.key.S:
        nave.speedX = 0
    elif symbol == pyglet.window.key.A:
        nave.speedZ = 0
        nave.rotationY = 0
    elif symbol == pyglet.window.key.D:
        nave.speedZ = 0
        nave.rotationY = 0

@controller.event
def on_mouse_motion(x, y, dx, dy): 
    if   dy > 0 and nave.positionY < 8: 
        nave.positionY += dy*18/HEIGHT
        nave.rotationZ = dy/2
    elif dy < 0 and nave.positionY > 0:
        nave.positionY += dy*18/HEIGHT
        nave.rotationZ = dy/2


@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    camera.update(controller, nave)
    #para el grafo
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "lightPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
    glUniform3f(glGetUniformLocation(controller.pipeline.shaderProgram, "viewPosition"), camera.eye[0], camera.eye[1], camera.eye[2])
    glUniform1ui(glGetUniformLocation(controller.pipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "constantAttenuation"), 0.0001)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "linearAttenuation"), 0.03)
    glUniform1f(glGetUniformLocation(controller.pipeline.shaderProgram, "quadraticAttenuation"), 0.01)


    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, camera.view)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    sg.drawSceneGraphNode(escena, controller.pipeline, "model")


def update(dt,controller, nave, obstaculos, escena):
    controller.total_time += dt
    nave.move(controller, escena, dt)
    for obstaculo in obstaculos:
        obstaculo.move(controller,escena, dt)

if __name__ == '__main__':
    pyglet.clock.schedule(update, controller, nave, obstaculos, escena)
    pyglet.app.run(1/60)
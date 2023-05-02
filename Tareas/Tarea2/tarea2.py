import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr
import libs.scene_graph as sg

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ

from OpenGL.GL import *

import objetos
import grafo

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 900, 900


class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"tarea2"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()

class Camera:
    def __init__(self, nave,
                 at  = np.array([0.0, 0.0, 0.0]),
                 eye = np.array([10.0, 0.0, 0.0]),
                 up  = np.array([0.0, 1.0, 0.0])
                 ):

        self.at  = at
        self.eye = eye
        self.up  = up

        self.projection = tr.ortho(-10, 10, -10, 10, 0.1, 100)
        self.view = tr.lookAt(self.at, self.eye, self.up)
        self.nave = nave

    def update(self):
        self.at = np.array([nave.posx, 0.0, nave.posz])
        self.eye = np.array([nave.posx+10, 0.0, nave.posz])
        self.view = tr.lookAt(self.at, self.eye, self.up)
    
controller = Controller(width=WIDTH, height=HEIGHT)

escena = grafo.grafo(controller.pipeline)
nave = objetos.Nave(escena)
obstaculos = objetos.Obstaculos(escena,(0,0,0),1)

camera = Camera(nave)


# Setting up the clear screen color
glClearColor(0.0, 0.0, 0.05, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)


@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()
    elif symbol == pyglet.window.key.W:
        nave.speedx = 4
    elif symbol == pyglet.window.key.S:
        nave.speedx = -4
    elif symbol == pyglet.window.key.A:
        nave.speedz = -4
    elif symbol == pyglet.window.key.D:
        nave.speedz = 4
@controller.event
def on_key_release(symbol, modifiers):
    if   symbol == pyglet.window.key.W:
        nave.speedx = 0
    elif symbol == pyglet.window.key.S:
        nave.speedx = 0
    elif symbol == pyglet.window.key.A:
        nave.speedz = 0
    elif symbol == pyglet.window.key.D:
        nave.speedz = 0


@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    camera.update()
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, camera.projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, camera.view)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())

    sg.drawSceneGraphNode(escena, controller.pipeline, "model")

    
# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt,controller, nave):
    controller.total_time += dt
    nave.move(dt)

if __name__ == '__main__':
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller, nave)
    # Set the view
    pyglet.app.run()
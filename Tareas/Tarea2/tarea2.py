import sys
import os
import pyglet
import numpy as np

import libs.shaders as sh
import libs.transformations as tr

from libs.gpu_shape import createGPUShape
from libs.obj_handler import read_OBJ
from libs.assets_path import getAssetPath

from OpenGL.GL import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

WIDTH, HEIGHT = 900, 900

assets = {
    "nave" : getAssetPath("nave.obj"),
    "obstaculo1": getAssetPath("crewmate.obj")
    }


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title=f"tarea2"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.dtt = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()

class Nave:
    def __init__(self,shape,color):
        self.shape = createGPUShape(controller.pipeline, read_OBJ(shape, color))

        self.speedrotation = 0
        self.rotation = 0

        self.speed = 0
        self.pos = 0
class Obstaculos:
    def __init__(self):
        pass


projection = tr.ortho(-10, 10, -10, 10, 0.1, 100)  # ORTOGRAPHIC_PROJECTION

view = tr.lookAt(
    at = np.array([0.0, 0.0, 0.0]),
    eye= np.array([1.0, 3.0, 5.0]),
    up = np.array([0.0, 0.0, 1.0])
    )

controller = Controller(width=WIDTH, height=HEIGHT)
nave = Nave(assets["nave"],(0.7, 0.2, 0.6))

# Setting up the clear screen color
glClearColor(0.1, 0.1, 0.1, 1.0)
glEnable(GL_DEPTH_TEST)
glUseProgram(controller.pipeline.shaderProgram)

###########################################Controles
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.ESCAPE:
        controller.close()
    elif symbol == pyglet.window.key.SPACE:
        nave.speedrotation = 10
    elif symbol == pyglet.window.key.A:
        nave.speed = -4
    elif symbol == pyglet.window.key.D:
        nave.speed = 4
@controller.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        nave.speedrotation = 0
    elif symbol == pyglet.window.key.A:
        nave.speed = 0
    elif symbol == pyglet.window.key.D:
        nave.speed = 0


@controller.event
def on_draw():
    controller.clear()
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    model = tr.matmul([tr.translate(2,nave.pos,0),tr.rotationX(nave.rotation),tr.rotationZ(np.pi),tr.rotationX(4*np.pi/10),tr.rotationY(np.pi/2)])

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, model)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    controller.pipeline.drawCall(nave.shape)


# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt,controller, nave):
    controller.total_time += dt
    nave.rotation += dt * nave.speedrotation
    nave.pos += dt*nave.speed

if __name__ == '__main__':
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller, nave)
    # Set the view
    pyglet.app.run()
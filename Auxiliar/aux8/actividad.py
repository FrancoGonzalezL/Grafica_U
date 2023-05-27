import pyglet
from OpenGL.GL import (glUseProgram, glClearColor, glEnable, GL_DEPTH_TEST,
                       glUniformMatrix4fv, glGetUniformLocation, GL_TRUE,
                       glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
                       glPolygonMode, GL_FRONT_AND_BACK, GL_FILL, GL_LINES)
import numpy as np
import grafica.transformations as tr
import grafica.basic_shapes as bs
import libs.shaders as sh
from grafica.gpu_shape import createGPUShape


WIDTH, HEIGHT = 800, 800


class Controller(pyglet.window.Window):
    def __init__(self, width, height, title=f"Curvas"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.pipeline = sh.SimpleModelViewProjectionShaderProgram()
        self.step = 0


controller = Controller(width=WIDTH, height=HEIGHT)

# Funciones de las curvas
def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def hermiteMatrix(P1, P2, T1, T2):

    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)

    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])

    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])

    return np.matmul(G, Mb)


# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)

    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)

    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T

    return curve


glClearColor(0.15, 0.15, 0.15, 1.0)

glEnable(GL_DEPTH_TEST)

glUseProgram(controller.pipeline.shaderProgram)

# Creating shapes on GPU memory
gpuAxis = createGPUShape(controller.pipeline, bs.createAxis(7))
gpuRedCube = createGPUShape(controller.pipeline, bs.createColorCube(1, 0, 0))
gpuGreenCube = createGPUShape(controller.pipeline, bs.createColorCube(0, 1, 0))
gpuBlueCube = createGPUShape(controller.pipeline, bs.createColorCube(0, 0, 1))
gpuYellowCube = createGPUShape(controller.pipeline, bs.createColorCube(1, 1, 0))
gpuCyanCube = createGPUShape(controller.pipeline, bs.createColorCube(0, 1, 1))
gpuPurpleCube = createGPUShape(controller.pipeline, bs.createColorCube(1, 0, 1))
gpuRainbowCube = createGPUShape(controller.pipeline, bs.createRainbowCube())


# Setting up the view transform
cam_radius = 10
camera_theta = np.pi/4
cam_x = cam_radius * np.sin(camera_theta)
cam_y = cam_radius * np.cos(camera_theta)
cam_z = cam_radius

viewPos = np.array([cam_x, cam_y, cam_z])

view = tr.lookAt(viewPos, np.array([0, 0, 0]), np.array([0, 0, 1]))

# Setting up the projection transform
projection = tr.ortho(-8, 8, -8, 8, 0.1, 100)

N = 3000

###                                            ###
### EN ESTA SECCIÓN DEFINIR Y CREAR LAS CURVAS ###
###                                            ###
tan = 2
pos = 2
# Creando una curva de Hermite
# Definimos los puntos
P1 = np.array([[-pos,   0, 0]]).T
P2 = np.array([[0,   -pos, 0]]).T
T1 = np.array([[0,   -tan, 0]]).T
T2 = np.array([[tan,    0, 0]]).T
GMh1 = hermiteMatrix(P1, P2, T1, T2)
P1 = np.array([[0,  -pos, 0]]).T
P2 = np.array([[pos,   0, 0]]).T
T1 = np.array([[tan,   0, 0]]).T
T2 = np.array([[0,   tan, 0]]).T
GMh2 = hermiteMatrix(P1, P2, T1, T2)
P1 = np.array([[pos,   0, 0]]).T
P2 = np.array([[0,   pos, 0]]).T
T1 = np.array([[0,   tan, 0]]).T
T2 = np.array([[-tan,  0, 0]]).T
GMh3 = hermiteMatrix(P1, P2, T1, T2)
P1 = np.array([[0,    pos, 0]]).T
P2 = np.array([[-pos,   0, 0]]).T
T1 = np.array([[-tan,   0, 0]]).T
T2 = np.array([[0,   -tan, 0]]).T
GMh4 = hermiteMatrix(P1, P2, T1, T2)

HermiteCurve = np.concatenate((evalCurve(GMh1, N//4),
                               evalCurve(GMh2, N//4),
                               evalCurve(GMh3, N//4),
                               evalCurve(GMh4, N//4)), axis=0)


###   AHORA SI YA TIENES LAS CURVAS DEFINIDAS   ###
###  TIENES QUE MODIFICAR UNA PARTE MÁS ABAJO   ###
### PARA QUE LOS CUBOS SE MUEVAS SEGUN LA CURVA ###


@controller.event
def on_draw():
    controller.clear()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    #                                                      #
    # AQUI SE ACTUALIZAN LOS STEPS Y SE REINICIA SU CUENTA #
    #                                                      #
    if controller.step >= N-200:
        controller.step = 0

    controller.step += 200

    ##### ENTRAREMOS EN MAS DETALLE SOBRE VIEW Y PROJECTION EN EL FUTURO #####

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    # Clearing the screen in both, color and depth
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    ##### DEBEN MODIFICAR ESTAS LINEAS PARA EL AUXILIAR 2 #####

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(5, 0, 0))
    controller.pipeline.drawCall(gpuRedCube)


    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0, 5, 0))
    controller.pipeline.drawCall(gpuBlueCube)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0, -5, 0))
    controller.pipeline.drawCall(gpuYellowCube)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0, 0, 5))
    controller.pipeline.drawCall(gpuCyanCube)

    ####                                                               ####
    #### MODIFICAR ESTA PARTE DEL CODIGO PARA AGREGAR LAS TRASLACIONES ####
    ####                                                               ####
    transformPurple = tr.matmul([ tr.translate(HermiteCurve[controller.step, 0], HermiteCurve[controller.step, 1], HermiteCurve[controller.step, 2])])
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformPurple)
    controller.pipeline.drawCall(gpuPurpleCube)


    transformRainbow = tr.identity()
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformRainbow)
    controller.pipeline.drawCall(gpuRainbowCube)

    transformGreen = tr.translate(-5, 0, 0)
    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, transformGreen)
    controller.pipeline.drawCall(gpuGreenCube)

    glUniformMatrix4fv(glGetUniformLocation(controller.pipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
    controller.pipeline.drawCall(gpuAxis, GL_LINES)


# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt


if __name__ == "__main__":
    # Try to call this function 60 times per second
    pyglet.clock.schedule(update, controller)
    # Set the view
    pyglet.app.run()

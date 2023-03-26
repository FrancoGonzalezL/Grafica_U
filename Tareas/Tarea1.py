import pyglet
from pyglet.window import Window, key, mouse
from pyglet.shapes import Circle, Rectangle, Star, Triangle
from pyglet.app import run
from pyglet.graphics import Batch

from random import randint
import numpy as np

window = Window(192*7, 108*7, "TAREA 1", resizable = True)
estrellasc = Batch()

class Estrellas:
    def __init__(self):
        self.posx  = randint(0,window.width)
        self.posy  = randint(0,window.height)
        self.puntas= randint(4,7)
        self.r_int = 1
        self.r_ext = randint(3,6)

        self.speed = randint(1,1000)/1500     

        self.cuerpo = Star(self.posx,self.posy,
                            outer_radius= self.r_ext, 
                            inner_radius = self.r_int,
                            num_spikes   = int(self.puntas),
                            color = (225,220,220),
                            batch = estrellasc)
    def move_down(self):
        self.cuerpo.y -= self.speed
        self.posy = self.cuerpo.y

    def up(self):
        if self.posy < -10:
            self.cuerpo.y = window.height+10
            self.posy = self.cuerpo.y    

#Creacion de los atributos para las n-estrellas
#posiciones y puntas aleatorias
num_estrellas = 750
estrellas = []
for i in range(num_estrellas):
    est = [Estrellas()]
    estrellas += est
estrellas = np.array(estrellas)




#for i in range(1):
#    estrell += [Estrellas(posiciones[i],puntas[i])]

class Naves:
    def __init__(self):
        pass

@window.event
def on_draw():

    window.clear()
    estrellasc.draw()
    
    for i in range(num_estrellas):
        estrellas[i].move_down()
        estrellas[i].up()





if __name__ == "__main__":
    run()


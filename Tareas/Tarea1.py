from pyglet.window import Window
from pyglet.shapes import Rectangle, Star, Triangle
from pyglet.app import run
from pyglet.graphics import Batch
from random import randint
import numpy as np
from math import cos
from time import time

window = Window(192*7, 108*7, "TAREA 1 Franco González Leiva", resizable = True)
batch = Batch()

class Estrellas:
    def __init__(self):
        #configuracion inicial aleatoria para las estrellas
        self.speed  = randint(1,1000)/1200
        self.cuerpo = Star( x = randint(0,window.width),
                            y = randint(0,window.height),
                            outer_radius= randint(1,4), 
                            inner_radius= 1,
                            num_spikes  = int(randint(4,7)),
                            color = (225,220,220),
                            batch = batch)
    #para que se muevan 
    def move_down(self):
        self.cuerpo.y -= self.speed
    #para que vuelvan arriba
    def up(self):
        if self.cuerpo.y < -10:
            self.cuerpo.y = window.height+10
            self.cuerpo.x = randint(0,window.width)


class Naves:
    def __init__(self,posx,posy,escala):
        self.posx = posx
        self.posy = posy
        self.escala = escala
        amar = (255,200,100)
        rojo = (125,0,0)
        gris = (65,65,65)
        col_ = (randint(0,255),randint(0,255),randint(0,255))

        self.cuerpo = np.array([ #cuerpo principal
                        Triangle(self.posx-4*self.escala,   self.posy,
                                self.posx+4*self.escala,    self.posy,
                                self.posx,                  self.posy+20*self.escala,
                                color=rojo, batch=batch),
                        Rectangle(self.posx-4*self.escala,  self.posy-11*self.escala,
                                width=8*self.escala,        height=11*self.escala,
                                color=rojo, batch=batch),
                        #fuego del motor
                        Triangle(self.posx-5*self.escala,   self.posy-14*self.escala,
                                self.posx-4*self.escala,    self.posy-18*self.escala,
                                self.posx-3*self.escala,    self.posy-14*self.escala,
                                color=amar, batch=batch),
                        Triangle(self.posx+5*self.escala,   self.posy-14*self.escala,
                                self.posx+4*self.escala,    self.posy-18*self.escala,
                                self.posx+3*self.escala,    self.posy-14*self.escala,
                                color=amar, batch=batch),
                        #ala izq
                        Rectangle(self.posx-13*self.escala, self.posy-9*self.escala,
                                width=8*self.escala,        height=8*self.escala,
                                color=rojo, batch=batch),
                        Triangle(self.posx-13*self.escala,  self.posy-9*self.escala,
                                self.posx-6*self.escala,    self.posy-9*self.escala,
                                self.posx-6*self.escala,    self.posy-11*self.escala,
                                color=rojo, batch=batch),
                        #ala der
                        Rectangle(self.posx+5*self.escala,  self.posy-9*self.escala,
                                width=8*self.escala,        height=8*self.escala,
                                color=rojo, batch=batch),
                        Triangle(self.posx+13*self.escala,  self.posy-9*self.escala,
                                self.posx+6*self.escala,    self.posy-9*self.escala,
                                self.posx+6*self.escala,    self.posy-11*self.escala,
                                color=rojo, batch=batch),
                        #canon centro
                        Rectangle(self.posx-0.5*self.escala,self.posy+17.5*self.escala,
                                width=1*self.escala,        height=2.4*self.escala,
                                color=gris, batch=batch),
                        #motor izq
                        Rectangle(self.posx-6*self.escala,  self.posy-5*self.escala,
                                width=4*self.escala,        height=5*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx-6*self.escala,  self.posy-12*self.escala,
                                width=4*self.escala,        height=5*self.escala,
                                color=gris,batch=batch),
                        Triangle(self.posx-6*self.escala,   self.posy-5*self.escala,
                                self.posx-4*self.escala,    self.posy-7*self.escala,
                                self.posx-2*self.escala,    self.posy-5*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx-6*self.escala,   self.posy-7*self.escala,
                                self.posx-4*self.escala,    self.posy-5*self.escala,
                                self.posx-2*self.escala,    self.posy-7*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx-6*self.escala,   self.posy-12*self.escala,
                                self.posx-4*self.escala,    self.posy-14*self.escala,
                                self.posx-2*self.escala,    self.posy-12*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx-5*self.escala,  self.posy-14*self.escala,
                                width=2*self.escala,        height=1*self.escala,
                                color=gris, batch=batch),
                        #motor der
                        Rectangle(self.posx+2*self.escala,  self.posy-5*self.escala,
                                width=4*self.escala,        height=5*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx+2*self.escala,  self.posy-12*self.escala,
                                width=4*self.escala,        height=5*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx+6*self.escala,   self.posy-5*self.escala,
                                self.posx+4*self.escala,    self.posy-7*self.escala,
                                self.posx+2*self.escala,    self.posy-5*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx+6*self.escala,   self.posy-7*self.escala,
                                self.posx+4*self.escala,    self.posy-5*self.escala,
                                self.posx+2*self.escala,    self.posy-7*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx+6*self.escala,   self.posy-12*self.escala,
                                self.posx+4*self.escala,    self.posy-14*self.escala,
                                self.posx+2*self.escala,    self.posy-12*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx+3*self.escala,  self.posy-14*self.escala,
                                width=2*self.escala,        height=1*self.escala,
                                color=gris, batch=batch),
                        #canon ala izquierda
                        Rectangle(self.posx-17*self.escala, self.posy-9*self.escala,
                                width=4*self.escala,        height=9*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx-17*self.escala, self.posy-10*self.escala,
                                width=4*self.escala,        height=1*self.escala,
                                color=rojo, batch=batch),
                        Rectangle(self.posx-16*self.escala, self.posy+4*self.escala,
                                width=1*self.escala,        height=5*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx-17*self.escala,  self.posy,
                                self.posx-16*self.escala,   self.posy+6*self.escala,
                                self.posx-13*self.escala,   self.posy,
                                color=rojo, batch=batch),
                        #canon ala derecha
                        Rectangle(self.posx+13*self.escala, self.posy-9*self.escala,
                                width=4*self.escala,        height=9*self.escala,
                                color=gris, batch=batch),
                        Rectangle(self.posx+13*self.escala, self.posy-10*self.escala,
                                width=4*self.escala,        height=1*self.escala,
                                color=rojo,batch=batch),
                        Rectangle(self.posx+15*self.escala, self.posy+4*self.escala,
                                width=1*self.escala,        height=5*self.escala,
                                color=gris, batch=batch),
                        Triangle(self.posx+17*self.escala,  self.posy,
                                self.posx+16*self.escala,   self.posy+6*self.escala,
                                self.posx+13*self.escala,   self.posy,
                                color=rojo, batch=batch),
                        #rectangulo superior de color random
                        Rectangle(self.posx-1*self.escala,  self.posy-9*self.escala,
                                width=2*self.escala,        height=9*self.escala,
                                color=col_, batch=batch)
                        ])

#creacion de las n-estrellas
num_estrellas = 800
estrellas = np.array(range(num_estrellas),dtype=object)
for i in range(num_estrellas):
    estrellas[i] = Estrellas()

#creacion de las naves
navx, navy = window.width//2, window.height//2
naves = np.array([Naves(navx    ,navy    ,4),
                  Naves(navx-200,navy-100,3),
                  Naves(navx+200,navy-100,3)])

@window.event
def on_draw():
    window.clear()
    batch.draw()

    #movimieto estrellas
    for estrella in estrellas:
        estrella.move_down()
        estrella.up()
    #animacion del fuego de las naves
    for nave in naves:
        nave.cuerpo[2].y2 = nave.posy-18*nave.escala + 2*cos(time()*4)
        nave.cuerpo[3].y2 = nave.posy-18*nave.escala + 2*cos(time()*4)

if __name__ == "__main__":
    run()
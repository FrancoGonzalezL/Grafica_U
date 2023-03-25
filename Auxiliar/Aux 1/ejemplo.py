import pyglet
from pyglet.window import Window, key
from pyglet.shapes import Circle, Rectangle
from pyglet.app import run
from pyglet.graphics import Batch

WIDTH = 1000
HEIGHT = 700
WINDOW_TITLE = 'auxiliar 1! ૮ ˶ᵔ ᵕ ᵔ˶ ა'
FULL_SCREEN = False
ventana = Window(WIDTH, HEIGHT, WINDOW_TITLE, resizable=True)
auto = Batch()
rueda0 = Circle(x=1.5*ventana.width//2, y=0.75*ventana.height//2, radius=70, color=(200, 200, 30), batch=auto)
rueda1 = Circle(x=0.75*ventana.width//2, y=0.75*ventana.height//2, radius=70, color=(200, 200, 30), batch=auto)
chasis = Rectangle(x=ventana.width//4, y=4*ventana.height//9, width=2*ventana.width//3, height=ventana.height//3, color=(20, 200, 20), batch=auto)


def enter_fullscreen(symbol, modifiers):
    if symbol == key.ENTER:
        ventana.set_fullscreen(not ventana._fullscreen)
ventana.on_key_press = enter_fullscreen

@ventana.event
def on_key_release(symbol, modifiers):
    if symbol == key.SPACE:
        ventana.set_fullscreen(not ventana._fullscreen)

@ventana.event
def on_draw():
    auto.draw()



run()



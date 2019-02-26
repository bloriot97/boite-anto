from enum import Enum
import evdev
import time


class TouchMouse():
    x=0
    y=0
    lastX=0
    lastY=0

    MOUSEPRETION = 1

    maxX=3564.0
    maxY=3770.0
    minX=354.0
    minY=346.0

    height = 320L
    width = 480L

    pressed = False

    verbose = True

    def __init__(self):
        self.device = evdev.InputDevice('/dev/input/event0')
        print(self.device.capabilities(verbose=True))

    def getEvents(self):
        event = self.device.read_one()
        self.lastX = self.x
        self.lastY = self.y
        events = []
        pressed = False
        released = False
        while (event):
            if ( event ) :
                #print(event)
                if ( event.type == self.MOUSEPRETION):
                    if ( event.value == 0):
                        self.pressed = False
                        released = True
                    else:
                        self.pressed = True
                        pressed = True
                elif ( event.type == 3):
                    if (event.code == 0 ):
                        self.x = (float(event.value) - self.minX) / (self.maxX - self.minX) * self.height
                    elif (event.code == 1 ):
                        self.y = (1-(float(event.value) - self.minY) / (self.maxY - self.minY)) * self.width
                    if ( self.verbose):
                        print("x:" , self.x, "  y:", self.y, self.pressed)
            event = self.device.read_one()
        if ( self.x != self.lastX or self.y != self.lastY):
            events.append("MOUSEMOTION")
        if ( pressed ):
            events.append("MOUSEDOWN")
        if ( released ):
            events.append("MOUSEUP")
        return events

    def getX(self):
        return self.y

    def getY(self):
        return self.x

if __name__ == '__main__':
    mouse = TouchMouse()
    while 1:
        print(mouse.getEvents())
        time.sleep(1)

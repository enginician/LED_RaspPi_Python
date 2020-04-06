import time
import board
import neopixel
import numpy as np
import random
#from random import seed
from random import randint
#seed(1)

LED_pin = board.D18 # Choose an open pin connected to the Data In of the NeoPixel strip, i.e. board.D18. NeoPixels must be connected to D10, D12, D18 or D21 to work.
num_pixels = 60 # The number of NeoPixels
ORDER = neopixel.GRB # The order of the pixel colors - RGB or GRB. Some NeoPixels have red and green reversed! For RGBW NeoPixels, simply change the ORDER to RGBW or GRBW.

pixels = neopixel.NeoPixel(LED_pin, num_pixels, brightness=0.3, auto_write = False, pixel_order = ORDER)
# Select the max brightnee as afloat from 0.0 to 1.0
# See Neopixel Python library documentation for further details: https://circuitpython.readthedocs.io/projects/neopixel/en/latest/api.html

# A class to "build" light dots. Dots can have a certain position on the LED strip,
# a size and other attributes

def sparkle():
    pixels[randint(0,num_pixels-1)] = (255,255,160)
    pixels.show()
    time.sleep(0.01)
    pixels.fill((0,0,0))
    
def bounceballs(ball, counter, offset):
    g = 9.81 # Erdbeschleunigung in m/s^2
    dissipation = 0 # factor in percent of how much of speed is lost due to dissipation energy when the ball bounces
                    # Technically this would need to be calculated based on energy approach, but to save us from a sqrt calculation this is just speed based and needs to be adjusted so that visuals look cool. This is no simulation :)
    v0 = 100
    ball.speed = v0 - (g*counter- offset)
    print ("ball speed is {} and ball position is {}".format(ball.speed, int(ball.pos)))
    print("g*counter/10 - offset is {}".format(g*counter/10 - offset))
    if int(ball.pos) <= 0 and ball.speed < 0:
        print("TRUE")
        ball.speed = -ball.speed
        v0 = ball.speed
        offset = g*counter/10
        return(offset)
        print("ball.speed ist jetzt {}".format(ball.speed))
    

class dot:
    def __init__(self, pos=0, color=[0,0,0], size=0, speed=0):
        
        self.color = color
        self.size = size
        self.pos = pos
        self.layer = np.array([])
        self.speed = speed #in pixel/second
        
    def updatepos(self):
        self.pos = (self.pos+(self.speed/100))
        if (self.pos+self.size) > num_pixels:
            self.pos = 0
        if self.pos < 0:
            self.pos = num_pixels-self.size
                    
    # calculating a vector that would be the output to the LED strip if only one instance of this obejct existed
    # If there are other instances, their color layer vectors will be merged in "def show()"
    def getlayer(self):
        self.updatepos()
        layer = []
        for x in range(num_pixels):
            if x < int(self.pos) or x >= (int(self.pos)+self.size):
                layer.insert(x, [0,0,0])           
            else:
                layer.insert(x,self.color)
        self.layer = np.array(layer)

# Computes resulting color vector from all color layers and send output to LED strip              
def show(outputbefore):
    output = 0
    
    # create vector "output" that contains light information for every pixel considering all light objects
    for x in range (len(dots)):
        dots[x].getlayer()
        output += dots[x].layer
    
    # consider light information from previous calc step to create light trace effect     
    for x in range(len(output)):
        if all(output[x] == 0) and any(outputbefore[x]!= 0):
            output[x] = outputbefore[x]*0.4
    
    # normalize if resultet color values exceed 255
    for i in range(output.shape[0]):
        m = max(output[i])
        if m >255:
            output[i] = [int(i/(m/255)) for i in output[i]]
            
    # send output to LED strip      
    for i in range(num_pixels):
        pixels[i] = tuple(output[i])
    pixels.show()
    
    # leave a light trace behind moving light objects
    outputbefore = output
#     print("~~~~~~~~~~~~~~~~~~~~~~~~~")
#     print("outputbefore is {}".format(outputbefore))
#     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
#     print("              END OF LOOP                ")
#     print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    return (outputbefore)

# Define functions which turns off LEDs when code is interrupted.
def turnoff(wait_ms):
    """Wipe color across display a pixel at a time."""
    for i in range(num_pixels):
        pixels[i] = (0,0,0)
        pixels.show()
        time.sleep(wait_ms/1000.0)

# Main program logic follows:
if __name__ == '__main__':
    print("Press Ctrl+c to turn off LEDs and exit")
    
    try:
        dots=[dot(color=[255,0,0]),dot(color=[0,255,0]),dot(color =[0,0,255]),
              dot(color=[255,0,0]),dot(color=[0,255,0]),dot(color =[0,0,255]),
              dot(color=[255,0,0]),dot(color=[0,255,0]),dot(color =[0,0,255]),
              dot(color=[255,0,0]),dot(color=[0,255,0]),dot(color =[0,0,255]),
               dot(color=[255,0,0]),dot(color=[0,255,0]),dot(color =[0,0,255])]        
#         dots=[dot(color=[255,0,0], size=2, speed=0, pos=1)]
        #ball = dots[0]
#               dot(color=[0,255,0], size=8, speed=-10, pos=0),
#               dot(color=[0,0,255], size=8, speed=20, pos=25),
#               dot(color=[125,125,0], size=2, speed=-30, pos=50),
#               dot(color=[0,125,125], size=2, speed=-45, pos=0),
#               dot(color=[125,0,125], size=2, speed=30, pos=10)]
        counter = 0 #timing counter to synchronize actions
        dotcounter = 0 # initialize counter that counts number of instances od LED dots
        dotindex = 0 # initialize dotindex
        offset = 0.0
        timer= randint(10,300)
        
        #initialize variable used for leaving light traces in show()
        outputbefore = []
        for x in range(num_pixels):
            outputbefore.append([0,0,0])
        outputbefore = np.array(outputbefore)
                                           
        while True:

            
            if counter == timer:
                dots.append(dot(color = [randint(0,255),randint(0,255),randint(0,255)]))
                dotcounter+=1
                print(dotcounter)
                
            if counter == timer:
                dots[dotindex].size = randint(2,8)
                dots[dotindex].speed = randint(-100,100)
                timer = randint(counter+50, counter +200)
                dotindex+=1
                if dotindex >= len(dots):
                    dotindex =0
                print ("timer updated and and dot #{} changed".format(dotindex)) 
            
            # calculate and send the output to the LED strip and exchange before value for light trace effect
            #offset = bounceballs(ball, counter, offset)
            outputbefore = show(outputbefore)
            time.sleep(0.01)
            counter+=1

#             sparkle()
              
    # if program is interrupted (e.g. through Ctrl+c), all pixels are turned off        
    except KeyboardInterrupt:
        turnoff(10)
        
        
        
        



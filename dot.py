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

pixels = neopixel.NeoPixel(LED_pin, num_pixels, brightness=1, auto_write = False, pixel_order = ORDER)
# Select the max brightnee as afloat from 0.0 to 1.0
# See Neopixel Python library documentation for further details: https://circuitpython.readthedocs.io/projects/neopixel/en/latest/api.html

# A class to "build" light dots. Dots can have a certain position on the LED strip,
# a size and other attributes

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos*3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos*3)
        g = 0
        b = int(pos*3)
    else:
        pos -= 170
        r = 0
        g = int(pos*3)
        b = int(255 - pos*3)
    return (r, g, b) if ORDER == neopixel.RGB or ORDER == neopixel.GRB else (r, g, b, 0)


def rainbow(wait):
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        time.sleep(wait)

def sparkle():
    pixels[randint(0,num_pixels-1)] = (255,255,160)
    pixels.show()
    time.sleep(0.05)
    pixels.fill((0,0,0))
    
def bounceballs():
   
    counter = [0,0,0,0,0,0]
    v0 = [300, 300, 300, 300, 300, 300]
    balls = [dot(color = [255,0,0], size = 2, pos=0,speed = v0[0]),
             dot(color = [0,255,0], size = 2, pos=0,speed = v0[1]),
             dot(color = [0,0,255], size = 2, pos=0,speed = v0[2]),
             dot(color = [255,255,0], size = 2, pos=0,speed = v0[3]),
             dot(color = [0,255,255], size = 2, pos=0,speed = v0[4]),
             dot(color = [255,0,255], size = 2, pos=0,speed = v0[5])]
    g = 7 # Erdbeschleunigung in m/s^2
    dissipation = [15, 20, 25, 30, 10, 5] # factor in percent of how much of speed is lost due to dissipation energy when the ball bounces
                    # Technically this would need to be calculated based on energy approach, but to save us from a sqrt calculation this is just speed based and needs to be adjusted so that visuals look cool. This is no simulation :)
    speedatbounce = [v0[0],v0[1], v0[2], v0[3], v0[4], v0[5]]
    
    while True:
        
        output = 0

        for x in range (len(balls)):
           
            if int(balls[x].pos) <= 0 and balls[x].speed < 0:
                print("BOUNCE")
                speedatbounce[x] = - balls[x].speed * (100 - dissipation[x])/100 - 2
                counter[x] = 0
                print("speedatbounce fuer {} ist jetzt {}".format(x,speedatbounce[x]))
                
            if int(balls[x].pos) < 1 and abs(balls[x].speed) < 10:
                speedatbounce[x] = v0[x]
                counter[x] = 0
                balls[x].pos = 0
                print("SHOOT")
            print("x ist {}, speedatbounce[x] ist {}, g ist {} und counter[x] ist {}".format(x, speedatbounce[x], g, counter[x]) )  
            balls[x].speed = speedatbounce[x]-(g*counter[x])  
            print ("ball speed is {} and ball position is {}".format(balls[x].speed, balls[x].pos))        
            counter[x] +=1
            
        showdots(balls)
        time.sleep(0.001)
#         if randint(0,4000) == 0:
#             return

    
class dot:
    def __init__(self, pos=0, color=[0,0,0], size=0, speed=0):
        
        self.color = color
        self.size = size
        self.pos = pos
        self.layer = np.array([])
        self.speed = speed #in pixel/second
        
    def updatepos(self):
        self.pos = (self.pos+(self.speed/100))
                    
    # calculating a vector that would be the output to the LED strip if only one instance of this obejct existed
    # If there are other instances, their color layer vectors will be merged in "def show()"
    def getlayer(self):
        self.updatepos()
        layer = []
        for x in range(num_pixels):
            if x < int(self.pos) or x > (int(self.pos)+self.size):
                layer.insert(x, [0,0,0])
            elif x == int(self.pos):
                layer.insert(x, [int(i * (1-(abs(self.pos-int(self.pos))))**3) for i in self.color])
            elif x == (int(self.pos) + self.size):
                layer.insert(x, [int(i * (abs(self.pos-int(self.pos)))**3) for i in self.color])
            else:
                layer.insert(x,self.color)

        self.layer = np.array(layer)
         
def showdots(dots):
    output = 0
    for x in range(len(dots)):
        dots[x].getlayer()
        output += dots[x].layer       
        # normalize if resulted color values exceed 255
        for i in range(output.shape[0]):
            m = max(output[i])
            if m >255:
                output[i] = [int(i/(m/255)) for i in output[i]]           
        for i in range(num_pixels):
            pixels[i] = tuple(output[i])
                
    pixels.show()
    

# Computes resulting color vector from all color layers and send output to LED strip
# this replaces the NeoPixel built-in pixels.show() and allows to overlay all effects in this code
def lighttrains():
    
    dots=[dot(color=[255,0,0], speed = 5),dot(color=[0,255,0], speed =2),
          dot(color =[0,0,255], speed = 1), dot(color=[255,0,0], speed = 10),
          dot(color=[0,255,0], speed = -8),dot(color =[0,0,255], speed = -3),
        dot(color=[255,0,0], speed = -10),dot(color=[0,255,0], speed =-5)]
        
    counter = 0 #timing counter to synchronize actions
    dotcounter = 0 # initialize counter that counts number of instances of LED dots
    dotindex = 0 # initialize dotindex
    timer= randint(10,300)
        
    #initialize variable used for leaving light traces in show()
    outputbefore = []
    for x in range(num_pixels):
        outputbefore.append([0,0,0])
    outputbefore = np.array(outputbefore)
    
    while True:
            
#         if counter == timer and dotcounter < 6:
#                     dots.append(dot(color = [randint(0,255),randint(0,255),randint(0,255)]))
#                     dotcounter+=1
#                     print(dotcounter)
                    
        if counter == timer:
            dots[dotindex].size = randint(2,8)
            dots[dotindex].speed = randint(-100,100)
            if dots[dotindex].speed >= 0:
                dots[dotindex].pos = 0 - dots[dotindex].size
            else:
                dots[dotindex].pos = num_pixels
            timer = randint(counter+50, counter +200)
            dotindex+=1
            if dotindex >= len(dots):
                dotindex =0
            print ("timer updated and and dot #{} changed".format(dotindex)) 
        
        output = 0
          
        # create vector "output" that contains light information for every pixel considering all light objects
        for x in range (len(dots)):
            # make the dots appear again on the other side of the LED strip once they exceed the LED strip
            if dots[x].pos > num_pixels:
               dots[x].pos = 0 - dots[x].size
            if dots[x].pos < (0-dots[x].size):
               dots[x].pos = num_pixels
            else:
                pass
           
            dots[x].getlayer()
            output += dots[x].layer
        
        # consider light information from previous calc step to create light trace effect     
        for x in range(len(output)):
            if all(output[x] == 0) and any(outputbefore[x]!= 0):
                output[x] = outputbefore[x]*0.5
        
        # normalize if resulted color values exceed 255
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
        
        time.sleep(0.001)
        counter+=1

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
#         test = [dot(color = [255,0,0], size = 3, pos =0, speed = 100)]
                                               
        while True:

            
            bounceballs()
#             rainbow(0.01)
#             rainbow(0.009)
#             rainbow(0.008)
#             rainbow(0.007)
#             rainbow(0.006)
#             rainbow(0.005)
#             rainbow(0.004)
#             rainbow(0.003)
#             rainbow(0.002)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)
#             rainbow(0.001)

              
    # if program is interrupted (e.g. through Ctrl+c), all pixels are turned off        
    except KeyboardInterrupt:
        turnoff(20)
        
        
        
        



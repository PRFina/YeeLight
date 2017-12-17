'''
Created on Feb 19, 2017

@author: prf
'''
import math

class YeeColor(object):
   
    def __init__(self,R=255,G=255,B=255):
        self.r=R
        self.g=G
        self.b=B
   
    def setRgb(self,R,G,B):
        self.r=R
        self.g=G
        self.b=B
   
    def rgbToInt(self):
        return (self.r*65536)+(self.g*255)+self.b



def colorLerp(clr1,clr2,bias):
    bias=clamp(bias, 0, 1)
    rint = clr1.r*(1-bias)+clr2.r*bias
    gint = clr1.g*(1-bias)+clr2.g*bias
    bint = clr1.b*(1-bias)+clr2.b*bias
    
    clrinterp=YeeColor(rint,gint,bint)
       
    return clrinterp


def kelvinToRgb(clrTemp):
    #TODO solve conversion errors
    clrTemp=clrTemp/100
    #Red computation
    if clrTemp < 66:
        red=255
    else:
        red=clrTemp - 60
        red= 329.698727466 *(red**(-0.1332047592))
        if red < 0:
            red=0
        elif red > 255:
            red=255
  
    #Green computation
    if clrTemp < 66:
        green=clrTemp
        green=99.4708025861 *math.log(green) - 161.1195681661

        if green < 0:
            green=0
        elif green > 255:
            green=255
    else:
        green= clrTemp-60
        green= 288.1221695283 * (green**(-0.0755148492))
        
        if green < 0:
            green=0
        elif green > 255:
            green=255
    
    #Blue computation
    if clrTemp >= 66:
        blue=255
    else:
        if clrTemp <= 19:
            blue=0
        else:
            blue=clrTemp-10
            blue=138.5177312231 * math.log(blue) - 305.0447927307

        if blue < 0:
            blue=0
        elif blue > 255:
            blue=255
            
    return (math.floor(red), math.floor(green), math.floor(blue))
       
            
            
                
def clamp(val,minValue,maxValue):
    if val>= minValue and val <=maxValue:
        return val
    elif val < minValue:
        return minValue
    elif val > maxValue:
        return maxValue
        
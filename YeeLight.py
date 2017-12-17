'''
Created on Feb 19, 2017

@author: prf
'''

import socket #for TCP-UDP/IP communication
import re #for regex

import YeeLightUtils as YL
from time import sleep
            
    
class YeeLight(object):

    def __init__(self,name="undefined"):
       
        #Identification Attributes
        self.YL_id=0
        self.name=name
        
        #Connection Attributes
        self.found=False
        self.connected=False
        self.servAddr="127.0.0.1"
        self.servPort=8080
        self.sock=-1
        
        #Status Attributes
        self.power=False
        self.bright=-1
        self.colorMode=-1
        self.colorRgb=-1
        self.colorHue=-1
        self.colorSat=-1
        self.colorTemp=-1
        
        
    def debugz(self):
        print("id:{0}\nfound:{1}\nconnected:{2}\nserver:{3}:{4}\nName:{5}\nPower:{6}\nBrightness:{7}\nColorMode:{8}\nColorTemp:{9}\nRGB:{10}\nHUE:{11}\nSaturation:{12}\n".format(
            self.YL_id,self.found,self.connected,self.servAddr,self.servPort,self.name,self.power,self.bright,self.colorMode,self.colorTemp,self.colorRgb,self.colorHue,self.colorSat))
    
     
    def validateConnectionMsg(self,msg):
        lines=msg.splitlines()
        print(lines)
        
        #search for header
        if lines[0] == "HTTP/1.1 200 OK":   
            self.found=True
        else:
            print("Error: Can't find any YeeLights device!")
        
        #Search for Location
        regex=re.search('([a-zA-Z]+):\s?([a-z]+)://([0-9.]+):([0-9.]+)',lines[4])
        if regex:
            self.servAddr=regex.group(3)
            self.servPort=regex.group(4)
        else:
            print("Error in parsing location")
                   
        #Search for id
        regex=re.search('([a-zA-Z]+):\s?(0x[0-9a-zA-Z]+)',lines[6])
        if regex:
            self.YL_id=regex.group(2)
        else:
            print("Error in parsing id")
        
        #Search for name
        regex=re.search('([a-zA-Z]+):\s?([0-9a-zA-Z]*)',lines[17])
        if regex:
            self.name=regex.group(2)
        else:
            print("Error in parsing name")
        
            
    def connect(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        #Build & Send multicast message (using UDP)
        srvAddr=("239.255.255.250",1982)
        msg="""M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1982\r\nMAN: "ssdp:discover"\r\nST: wifi_bulb\r\n"""
        sock.sendto(msg.encode('utf_8'),srvAddr)
        
        #Receive and parse 
        welcomeData= sock.recvfrom(4096) 
        self.validateConnectionMsg(welcomeData[0].decode("utf_8"))
        sock.close()
       
        #Establish TCP connection
        self.sock= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.sock.connect((self.servAddr,int(self.servPort)))
        self.connected=True

    def update(self):
        sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        
        #Build & Send multicast message (using UDP)
        srvAddr=("239.255.255.250",1982)
        msg="""M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1982\r\nMAN: "ssdp:discover"\r\nST: wifi_bulb\r\n"""
        sock.sendto(msg.encode('utf_8'),srvAddr)
        
        #Receive msg and split in 
        welcomeData= sock.recvfrom(4096)
        msgLines=welcomeData[0].decode("utf-8").splitlines()
        
        
        #Parsing Power
        regex=re.search('(power|Power):\s?(on|On|ON|off|Off|OFF)',msgLines[10])
        if regex:
            status=regex.group(2)
            if status == "on" or status == "On" or status == "ON":
                self.power = True
            else:
                self.power = False
        else:
            print("Error in parsing power status")
        
        #Parsing Brightness  
        regex=re.search('(bright|Bright):\s?([0-9]+)',msgLines[11])
        
        if regex:
            self.bright = int(regex.group(2))
        else:
            print("Error in parsing brightness status")
            
        #Parsing color mode
        regex=re.search('(color_mode|Color_mode):\s?(1|2|3)',msgLines[12])
        if regex:
            self.colorMode = int(regex.group(2))
        else:
            print("Error in parsing color mode status")
        
        #Parsing color temperature
        regex=re.search('(ct|Ct\CT):\s?([0-9]+)',msgLines[13])
        if regex:
            self.colorTemp = int(regex.group(2))
        else:
            print("Error in parsing color temperature status")
         
        #Parsing color RGB
        regex=re.search('(rgb|Rgb\RGB):\s?([0-9]+)',msgLines[14])
        if regex:
            self.colorRgb = int(regex.group(2))
        else:
            print("Error in parsing rgb color status")
        
        #Parsing color HUE
        regex=re.search('(hue|Hue\HUE):\s?([0-9]+)',msgLines[15])
        if regex:
            self.colorHue = int(regex.group(2))
        else:
            print("Error in parsing HUE color status")
        
        #Parsing color saturation
        regex=re.search('(sat|Sat\saturation):\s?([0-9]+)',msgLines[16])
        if regex:
            self.colorSat = int(regex.group(2))
        else:
            print("Error in parsing color saturation status")
        
    def disconnect(self):
        self.sock.close()
   
    def setRGB(self,clr,dTime=500,mode="smooth"):
       
        cmdMsg="""{"id":1,"method":"set_rgb","params":[%d,"%s",%d]}\r\n"""%(clr.rgbToInt(), mode, dTime)
        self.sock.send(cmdMsg.encode('utf_8'))
       
        data=self.sock.recv(1024)
        print(data) 

    def setHSV(self,hue,saturation,dTime=500,mode="smooth"):
        
        YL.clamp(hue, 0, 359)
        YL.clamp(saturation,0,100)
        
        cmdMsg="""{"id":1,"method":"set_hsv","params":[%d,%d,"%s",%d]}\r\n"""%(hue, saturation, mode,dTime)
       
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)   
    
    def setTemp(self, kelvin,dTime=500,mode="smooth"):
       
        kelvin=YL.clamp(kelvin, 1700, 40000)
        
        if kelvin < 6500:
            cmdMsg="""{"id":1,"method":"set_ct_abx","params":[%d,"%s",%d]}\r\n"""%(kelvin, mode, dTime)
            self.sock.send(cmdMsg.encode('utf_8'))
            data=self.sock.recv(1024)
            print(data)   
        else:
            r,g,b=YL.kelvinToRgb(kelvin)
            self.setRGB(r,g,b,dTime,mode)
            
            
    def setBright(self,value, dTime=500,mode="smooth"):
        
        dTime= 1000
        value=YL.clamp(value, 0, 100)
        cmdMsg="""{"id":1,"method":"set_bright","params":[%d,"%s",%d]}\r\n"""%(value, mode, dTime)
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)
        
    def setPowerOn(self, dTime=500,mode="smooth"):

        cmdMsg="""{"id":1,"method":"set_power","params":["on","%s",%d]}\r\n"""%(mode, dTime)
        
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)   
    
    def setPowerOff(self, dTime=500, mode="smooth"):

        cmdMsg="""{"id":1,"method":"set_power","params":["off","%s",%d]}\r\n"""%(mode, dTime)
        
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)     
    
    def addCronoJob(self,time):
       
        cmdMsg="""{"id":3,"method":"cron_add","params":[0,%d]}\r\n"""%(time)
        
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)     
    
    def flow(self):
        cmdMsg="""{"id":2,"method":"start_cf","params":[3, 0,"1000, 2, 3700,100,3000, 2, 1800,100"]}\r\n"""
        
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data) 
    
    def colorWheel(self,time,dAngle=6,anglePhase=0):
        angle=0
        angle+=anglePhase
        
        for i in range(0,60*time):
            self.setHSV(angle, 100,1000)  
            angle = (angle+dAngle)%360
            sleep(1)
            
    def setName(self,newName):
       
        cmdMsg="""{"id":5,"method":"set_name","params":["%s"]}\r\n"""%(newName)
        #self.name=newName
        self.sock.send(cmdMsg.encode('utf_8'))
        data=self.sock.recv(1024)
        print(data)    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

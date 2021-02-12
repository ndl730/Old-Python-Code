import time
import random
import bibliopixel
from bibliopixel.drivers.visualizer import *
from bibliopixel.drivers.serial_driver import *
from bibliopixel.led import *
import pyaudio
import wave
import numpy as np
from struct import unpack
from math import *
import bibliopixel.image as image
import sys
from decimal import *

#default placeholder values to be overwritten
class main(object):
    visw = 40
    vish = 20
    idevice = 2
    chunk = 4096
    yshift = 700
    bandc = 1.00185
    logc = 1.35
    powshift = 100
    wscale = 900000
    freqrange = 83
    srate = 96000
    dropfactor = 2
    sens = 0
    pixsize = 10
    brightness = 100

    #command line arguments
    def initialize(self):
        self.visw = int(sys.argv[2])
        self.vish = int(sys.argv[3])
        self.idevice = int(sys.argv[4])
        self.chunk = int(sys.argv[5])
        self.yshift = int(sys.argv[6])
        self.bandc = Decimal(sys.argv[7])
        self.logc = Decimal(sys.argv[8])
        self.powshift = int(sys.argv[9])
        self.wscale = int(sys.argv[10])
        self.freqrange = int(sys.argv[11])
        self.srate = int(sys.argv[12])
        self.dropfactor = Decimal(sys.argv[13])
        self.sens = Decimal(sys.argv[14])
        self.pixsize = int(sys.argv[15])
        self.brightness = int(sys.argv[16])
        
        self.startemu(sys.argv[1])

    #start options
    def startemu(self, option):
        i = initled()
        o = output()

        if option == "emulated":
            i.ledemu(self.visw, self.vish, self.pixsize)
        elif option == "double":
            i.leddouble(self.visw, self.vish, self.brightness)
        elif option == "single":
            i.ledsingle(self.visw, self.vish, self.brightness)

        o.mainloop(self.idevice, self.yshift, self.visw, self.vish, self.bandc, self.logc, self.powshift, self.wscale, self.freqrange, self.chunk, i.led, self.srate, self.dropfactor, self.sens)

#display options
class initled(object):
    #emulaton with driver visualizer
    def ledemu(self, visw, vish, pixsize):
        #set log
        bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
        #create drivervisualizer instance
        driver = DriverVisualizer(width=visw, height=vish, pixelSize=pixsize)
        #create and orient display
        self.led = LEDMatrix(driver, vert_flip=True)
        #set texture
        texture1 = image.loadImage(self.led, "texture2.jpg")
        self.led.setTexture(tex=texture1)

    #display with single bibliopixel (unfinished)
    def ledsingle(self, visw, vish, brightness):
        m = MultiMapBuilder()
        m.addRow(mapGen(int(visw/2),vish,rotation=MatrixRotation.ROTATE_90),mapGen(int(visw/2),vish,rotation=MatrixRotation.ROTATE_90))
        bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
        driver1 = DriverSerial(num = 200, type = LEDTYPE.WS2811, deviceID = 3)
        led1 = LEDMatrix(driver1, width=20, height=10, coordMap = m.map, rotation=MatrixRotation.ROTATE_0, masterBrightness=255, pixelSize=(1,1))
        texture1 = image.loadImage(led1, "texture2.jpg")
        led1.setTexture(tex=texture1)

    #display with multiple bibliopixel
    def leddouble(self, visw, vish, brightness):
        #create multimapbuilder instance for multiple allpixels
        m = MultiMapBuilder()
        #orient both allpixels correctly
        m.addRow(mapGen(int(visw/2),vish,rotation=MatrixRotation.ROTATE_270),mapGen(int(visw/2),vish,rotation=MatrixRotation.ROTATE_270,vert_flip=True))
        bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
        #instances for both allpixels
        driver1 = DriverSerial(num = 400, type = LEDTYPE.WS2811, deviceID = 1)
        driver2 = DriverSerial(num = 400, type = LEDTYPE.WS2811, deviceID = 2)
        #display using two drivers
        self.led = LEDMatrix([driver2,driver1], width=visw, height=vish, coordMap = m.map, rotation=MatrixRotation.ROTATE_0, masterBrightness=brightness, pixelSize=(1,1))
        texture1 = image.loadImage(self.led, "texture2.jpg")
        self.led.setTexture(tex=texture1)

#output class
class output(object):
    #main loop for output on spectrum analyzer
    def mainloop(self, idevice, yshift, visw, vish, bandc, logc, powshift, wscale, freqrange, chunk, led, srate, dropfactor, sens):
        #audio options
        s = pyaudio.PyAudio()
        sound = s.open(format = pyaudio.paInt16, channels = 2, rate = srate, input = True, frames_per_buffer = chunk, input_device_index=idevice)
        data = sound.read(chunk)

        #create drop anmiation array size of spectrum analyzer width
        temp = [visw]
        for x in range(0,visw):
            temp.append(0)

        #begin loop
        vol = 100000
        while True:
            #read audio
            data = sound.read(chunk)
            data = unpack("%dh"%(len(data)/2),data)
            data = np.array(data,dtype='h')
            data = abs(np.fft.rfft(data))
            #apply volume
            data = data/vol

            if np.mean(temp) <= int(vish/4) and vol > 5000:
                vol -= 1000
            else:
                vol += 1000
            
            #process how sound shold be displayed
            y = yshift
            for z in range(0,visw):
                #check if sound is loud enough to be displayed
                if log(data[int(pow(bandc,y))], logc) < sens:
                    #do not display if too quiet
                    t = 0
                else:
                    #move audio in to bands
                    t = int(log(data[int(pow(bandc,y))], logc)+(math.pow(y+powshift,2)/wscale))

                #check if value should be displayed
                if t > temp[z]:
                    temp[z] = t

                #display band
                led.fillRect(z,0,1,int(temp[z]))
                y=y+freqrange

                #apply dropping animation
                if temp[z] >= 1:
                    factor = dropfactor
                    temp[z] = temp[z] - factor

            #update display
            led.update()
            led.all_off()

#instance of main class
m = main()
m.initialize()

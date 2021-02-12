import time
import random
import bibliopixel
from bibliopixel.drivers.serial_driver import *
from bibliopixel.drivers.visualizer import *
from bibliopixel.led import *
import pyaudio
import wave
import numpy as np
from struct import unpack
from math import *
import bibliopixel.image as image

m = MultiMapBuilder()
m.addRow(mapGen(10,10,rotation=MatrixRotation.ROTATE_90),mapGen(10,10,rotation=MatrixRotation.ROTATE_90))
bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
driver1 = DriverSerial(num = 200, type = LEDTYPE.WS2811, deviceID = 3)
led1 = LEDMatrix(driver1, width=20, height=10, coordMap = m.map, rotation=MatrixRotation.ROTATE_0, masterBrightness=150, pixelSize=(1,1))
texture1 = image.loadImage(led1, "texture2.jpg")
led1.setTexture(tex=texture1)
chunk = 4096

s = pyaudio.PyAudio()
sound = s.open(format = pyaudio.paInt16, channels = 2, rate = 96000, input = True, frames_per_buffer = chunk, input_device_index=1)
data = sound.read(chunk)

temp = [20]
for x in range(0,20):
    temp.append(0)

vol = 1000000
while True:
    data = sound.read(chunk)
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data,dtype='h')
    data = abs(np.fft.rfft(data))
    data = data/vol

    y = 300
    for z in range(0,20):
        if log(data[int(pow(1.00185,y))], 1.35) < -10:
            t = 0
        else:
            t = int(log(data[int(pow(1.00185,y))], 1.35)+(pow(y+100,2)/900000))

        if t > temp[z]:
            temp[z] = t
            
        led1.fillRect(z,0,1,int(temp[z]))
        y=y+163

        if temp[z] >= 1:
            factor = 1
            temp[z] = temp[z] - factor

    led1.update()
    led1.all_off()

sound.stop_stream()

sound.close()
s.terminate()

import time
import random
import bibliopixel
from bibliopixel.drivers.serial_driver import *
from bibliopixel.led import *
import pyaudio
import wave
import numpy as np
from struct import unpack
from math import *
import bibliopixel.image as image

m = MultiMapBuilder()
m.addRow(mapGen(20,20,rotation=MatrixRotation.ROTATE_270),mapGen(20,20,rotation=MatrixRotation.ROTATE_270,vert_flip=True))
bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
driver1 = DriverSerial(num = 400, type = LEDTYPE.WS2811, deviceID = 1)
driver2 = DriverSerial(num = 400, type = LEDTYPE.WS2811, deviceID = 2)
led1 = LEDMatrix([driver2,driver1], width=40, height=20, coordMap = m.map, rotation=MatrixRotation.ROTATE_0, masterBrightness=100, pixelSize=(1,1))
texture1 = image.loadImage(led1, "texture2.jpg")
led1.setTexture(tex=texture1)
chunk = 4096

s = pyaudio.PyAudio()
sound = s.open(format = pyaudio.paInt16, channels = 2, rate = 96000, input = True, frames_per_buffer = chunk, input_device_index=2)
data = sound.read(chunk)

temp = [40]
for x in range(0,40):
    temp.append(0)

vol = 100000
while True:
    data = sound.read(chunk)
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data,dtype='h')
    data = abs(np.fft.rfft(data))
    data = data/vol

    if np.mean(temp) <= 10 and vol > 30000:
        vol -= 1000
    else:
        vol += 1000

    y = 300
    for z in range(0,40):
        if log(data[int(pow(1.00185,y))], 1.35) < -50:
            t = 0
        else:
            t = int(log(data[int(pow(1.00185,y))], 1.35)+(pow(y+100,2)/900000))

        if t > temp[z]:
            temp[z] = t
            
        led1.fillRect(z,0,1,int(temp[z]))
        y=y+83

        if temp[z] >= 1:
            factor = 1
            temp[z] = temp[z] - factor

    led1.update()
    led1.all_off()

sound.stop_stream()

sound.close()
s.terminate()

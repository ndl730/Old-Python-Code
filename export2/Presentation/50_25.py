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

coords2 = mapGen(50,13)
coords1 = mapGen(50,12)
bibliopixel.log.setLogLevel(bibliopixel.log.DEBUG)
driver1 = DriverSerial(num = 600, type = LEDTYPE.WS2811, deviceID = 4)
driver2 = DriverSerial(num = 650, type = LEDTYPE.WS2811, deviceID = 5)
led1 = LEDMatrix(driver1, width=50, height=12, coordMap = coords1, rotation=MatrixRotation.ROTATE_180, masterBrightness=250, pixelSize=(1,1))
led2 = LEDMatrix(driver2, width=50, height=13, coordMap = coords2, rotation=MatrixRotation.ROTATE_180, masterBrightness=250, pixelSize=(1,1))
texture1 = image.loadImage(led1, "texture2.jpg", offset=(0,0))
texture2 = image.loadImage(led2, "texture2.jpg", offset=(0,-12))
led1.setTexture(tex=texture1)
led2.setTexture(tex=texture2)
chunk = 4096

s = pyaudio.PyAudio()
sound = s.open(format = pyaudio.paInt16, channels = 2, rate = 96000, input = True, frames_per_buffer = chunk, input_device_index=2)
data = sound.read(chunk)

temp = [50]
for x in range(0,50):
    temp.append(0)

vol = 100000
while True:
    data = sound.read(chunk)
    data = unpack("%dh"%(len(data)/2),data)
    data = np.array(data,dtype='h')
    data = abs(np.fft.rfft(data))
    data = data/vol

    if np.mean(temp) <= 12 and vol > 30000:
        vol -= 1000
    else:
        vol += 1000

    y = 300
    for z in range(0,50):
        if log(data[int(pow(1.00185,y))], 1.3) < -50:
            t = 0
        else:
            t = int(log(data[int(pow(1.00185,y))], 1.3)+(pow(y+100,2)/800000))

        if t > temp[z]:
            temp[z] = t
            
        led1.fillRect(z,0,1,int(temp[z]))
        led2.fillRect(z,-1,1,int(temp[z])-12)
        y=y+64

        if temp[z] >= 1:
            factor = 1
            temp[z] = temp[z] - factor

    led1.update()
    led1.all_off()
    led2.update()
    led2.all_off()

sound.stop_stream()

sound.close()
s.terminate()

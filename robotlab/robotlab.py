import serial
import time


p = serial.Serial("COM3", timeout=0.5)

while True:
    data = p.read(8)
    print(bytearray(data))


\xce\xfd\xd9\xef\xf5\xf8

110011101111 11011101 10011110 1111 1111 0101 1111 100
DD
11011101

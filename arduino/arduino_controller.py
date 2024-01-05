import serial
import time

arduino = serial.Serial(port='COM4',  baudrate=9600, timeout=.1)

def write_read(x):
    arduino.write(bytes(x,  'utf-8'))
    time.sleep(2)
    data = arduino.readline()
    return  data

while True:
    print("High")
    write_read('H')
    print("Low")
    write_read("L")
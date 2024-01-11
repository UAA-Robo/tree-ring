import serial.tools.list_ports
import serial
import time

port = ""
for p in list(serial.tools.list_ports.comports()):
    if "CH340" in p.description:
        port = p.device
        break

arduino = serial.Serial(port=port,  baudrate=9600, timeout=.1)

def write_read(x):
    arduino.write(bytes(x,  'utf-8'))
    time.sleep(2)
    data = arduino.readline()
    return  data

time.sleep(2)
arduino.write(bytes('Z',  'utf-8'))
while True:
    time.sleep(0.5)
    print(arduino.readline())
'''
while True:
    print("High")
    print(write_read('H'))
    print("Low")
    print(write_read("L"))
'''
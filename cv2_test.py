import cv2
cam = cv2.VideoCapture(cv2.CAP_FIREWIRE + 0)
while True:
    ret_val, img = cam.read()
    if img:
        cv2.imshow('test', img)
    else:
        print("No image")
    if cv2.waitKey(1) == 27: 
        break  # esc to quit
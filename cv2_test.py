import cv2
# print(cv2.getBuildInformation())

cam = cv2.VideoCapture(0, cv2.CAP_FIREWIRE)
while True:
    ret_val, img = cam.read()
    if img:
        cv2.imshow('test', img)
    else:
        print("No image")
    if cv2.waitKey(1) == 27: 
        break  # esc to quit
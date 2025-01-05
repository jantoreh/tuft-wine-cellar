import time
from led import set_color, Color
from picamera2 import Picamera2, Preview



picam2 = Picamera2()
camera_config = picam2.create_preview_configuration()
capture_config = picam2.create_still_configuration({"size": (1024, 1024)})
picam2.configure(capture_config)

none = Color(0, 0, 0)
white = Color(255, 255, 255)
red = Color(255, 0, 0)
green = Color(0, 255, 0)

def camera_light():
    set_color(white, brightness=20)

def set_ok():
    set_color(green, brightness=20)
    time.sleep(1)
    set_inactive()

def set_inactive():
    set_color(none)

def set_failed():
    set_color(red, brightness=20)
    time.sleep(1)
    set_inactive()

def get_image(path="img.png"):
    camera_light()
    picam2.start()
    time.sleep(1)
    picam2.capture_file(path)
    set_inactive()
    return path

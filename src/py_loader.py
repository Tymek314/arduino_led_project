import serial
import time

list_L = []
list_R = []
brightness_L = "020"
brightness_R = "020"


esp32 = serial.Serial("COM9", 115200, timeout=1)
print(f"Connected to {esp32.port}")
time.sleep(2)


def load_pixels():
    out_str : str = ""

    out_str += "R"
    out_str += brightness_R
    for r in list_R:
        out_str += r

    out_str += "L"
    out_str += brightness_L
    for l in list_L:
        out_str += l

    print(out_str)
    esp32.write((out_str + "\n").encode())

    if esp32.in_waiting:
        response = esp32.read(esp32.in_waiting)
        print(f"ESP32 response: {response.decode(errors='ignore')}")
    else:
        print("No response from ESP32")

#install tesseract for windows https://github.com/UB-Mannheim/tesseract/wiki
#pip3 install pytesseract
#pip3 install opencv-python


import cv2
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import Output
import numpy as np
from PIL import ImageGrab
import os
import time
import win32api, win32con
import argparse
import pynput
from pynput.keyboard import Key, Controller


keyboard = Controller()


class mouse():
    def leftClick(x, y):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y)
        time.sleep(.1)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y)
        print("Left Click: {}, {}".format(x, y))


    def setPos(x, y):
        win32api.SetCursorPos((x, y))
     

    def get_cords():
        x,y = win32api.GetCursorPos()
        print('Got mouse coordinates at: {}, {}'.format(x,y))

def getTesseractPath():
    if os.path.exists("tesseract_path.txt"):
        f = open("tesseract_path.txt", "r")
        tPath = f.read()
        pytesseract.pytesseract.tesseract_cmd = tPath
    else:
        print('ERROR: Could not find the tesseract path. Please make sure it is installed.')
        exit(code=0)


def screenGrab(color=False):
    img = ImageGrab.grab()
    if not color:
        img = convertToBnW(img)
    return img


def convertToBnW(img):
    gray = img.convert('1')

    return gray


def findButtonByColor(color):
    found_color = False
    while not found_color:

        img = screenGrab(True)

        x_coords = []
        y_coords = []
        for x in range(1, img.width): # Iterate through all pixels in the image
            for y in range(1, img.height):
                if img.getpixel((x, y)) == color: # If the pixel is not transparent
                    # Add the coordinates of the pixel to a list
                    x_coords.append(x)
                    y_coords.append(y)

        if len(x_coords) > 1 and len(y_coords) > 1:
            # Calculate the bounds of the non-transparent item from our lists
            left = min(x_coords)   
            top = min(y_coords)
            right = max(x_coords)
            bottom = max(y_coords)

            print('Button bounding box: {}, {} x {}, {}'.format(top,left, bottom,right))

            # Return coordinates at the center of the button
            x = ((right-left)/2)+left
            y = ((bottom-top)/2)+top
            
            print('Button center located at: {}, {}'.format(x, y))
            found_color = True

            return int(x), int(y)
        
        time.sleep(0.1)


def findButtonByText(text):
    found_text = False
    print('Searching for "{}" button...'.format(text))
    while not found_text:
        
        data = pytesseract.image_to_data(screenGrab(True), lang='eng', output_type=Output.DICT)

        i = 0
        for string in data['text']:
            if text.lower() == string.lower():
                found_text = True

                left = int(data['left'][i])
                top = int(data['top'][i])
                right = int(data['left'][i]) + int(data['width'][i])
                bottom = int(data['top'][i]) + int(data['height'][i])

                print('Button bounding box: {}, {} x {}, {}'.format(top,left, bottom,right))
                
                x = ((right-left)/2)+left
                y = ((bottom-top)/2)+top

                print('Button center located at: {}, {}'.format(x, y))

                return int(x), int(y)

            i+=1
        time.sleep(0.05)
    

def findText(screenshot, text):
    ocr = pytesseract.image_to_string(screenshot, lang='eng')
    for string in text:
        if string.lower() in ocr.lower():
            print('Found text "{}"'.format(string))
            return True
        
    return False


def launchGame():
    os.system('start steam://rungameid/376210')


def waitForText(text):
    found_text = False
    print('Waiting for text: {}...'.format(text))
    while not found_text:
        
        screenshot = screenGrab(False)
        if findText(screenshot, text):
            found_text = True
        time.sleep(0.05)


def main():
    # Get paths and arguments
    getTesseractPath()
    parser = argparse.ArgumentParser(description='A bot that will continue attempting to join The Isle servers until it gets in.')
    parser.add_argument('--server', metavar='S', type=str, required=True, nargs=1,
                        help='The name of the server you want to queue up')
    parser.add_argument('--sms', type=int,
                        help='10-digit phone number you want an SMS notification sent to when successfully connected to the server')
    parser.add_argument('--email', type=str,
                        help='Email address you want a notification sent to when successfully connected to the server')

    args = parser.parse_args()
    
    # Start the game and wait for the disclaimer
    print('Launching The Isle')
    launchGame()
    waitForText(["I understand", "EVRIMA", "Greetings"])

    # Click "I understand"
    x, y = findButtonByColor((99,168,131))
    mouse.setPos(x, y)
    time.sleep(1)
    mouse.leftClick(x,y)

    # Click "Play"
    x, y = findButtonByText("Play")
    mouse.setPos(x, y)
    time.sleep(1)
    mouse.leftClick(x,y)

    # Find the Filter input box
    print('Waiting for servers to load...')
    x, y = findButtonByColor((155,179,174))
    mouse.setPos(x, y)
    time.sleep(1)
    mouse.leftClick(x,y)

    # Enter the server name
    time.sleep(0.5)
    keyboard.type(str(args.server[0]))

    # Connect to the server
    print("Analyzing search results...")
    x, y = findButtonByColor((73,203,174))
    mouse.setPos(x, y)
    time.sleep(1)
    mouse.leftClick(x,y)
    time.sleep(0.2)
    mouse.leftClick(x,y)


if __name__ == '__main__':
    main()
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
from datetime import datetime
import win32api, win32con
import argparse
import pynput
import psutil
from pynput.keyboard import Key, Controller


keyboard = Controller()


class Notification():

    def __init__(self, type="", contact=""):
        print("Notifications will be sent to {}".format(contact))
        self.type = type
        self.contact = contact
    

    def send(self):
        if self.type == "SMS":
            print('Sending SMS to: {}'.format(self.contact))
        elif self.type == "Email":
            print('Sending Email to: {}'.format(self.contact))

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


def killTheIsle():
    PROCNAME = "TheIsleClient-Win64-Shipping.exe"
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()

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


def findButtonByText(text):

    print('Searching for "{}" button...'.format(text))

    while True:

        data = pytesseract.image_to_data(screenGrab(True), lang='eng', output_type=Output.DICT)
        i = 0

        for string in data['text']:
            if text.lower() == string.lower():
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


def waitForText(text, timeout=0, debug=False):
    print('Waiting for text: {} timeout in {}s...'.format(text, timeout))

    if timeout:
        start = time.time()

    while True:
        img = screenGrab(True)
        data = pytesseract.image_to_data(img, lang='eng', output_type=Output.DICT)
        if debug:
            print(data)
            img.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) + '.png', 'PNG')

        
        for search_string in text:
            i = 0
            for ocr_string in data['text']:
                if search_string.lower() in ocr_string.lower():
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

        if timeout and (time.time() - start) > timeout:
            # Close the game and call main()
            print("Sorry, we've run in to a problem. Islebot is starting over...")
            killTheIsle()
            main()
            return False

def launchGame():
    os.system('start steam://rungameid/376210')


def connectionLoop(server, timeout=0):

    if timeout:
        start = time.time()

    while True: 
        # Click "Play"
        x, y = findButtonByText("Play")
        mouse.setPos(x, y)
        time.sleep(1)
        mouse.leftClick(x,y)

        # Find the Filter input box
        print('Waiting for servers to load...')
        x, y = findButtonByColor((155,179,174))
        #x, y = findButtonByText("Filter")
        mouse.setPos(x, y)
        time.sleep(1)
        mouse.leftClick(x,y)

        # Enter the server name
        time.sleep(0.5)
        keyboard.type(server)

        # Connect to the server
        print("Analyzing search results...")
        x, y = findButtonByColor((73,203,174)) # Click the server result
        mouse.setPos(x, y)
        time.sleep(1)
        mouse.leftClick(x,y)
        time.sleep(0.2)
        mouse.leftClick(x,y)

        # Did we connect successfully?
        if waitForText(["Herbivore", "Carnivore", "Eggs", "Humans", "ASSET", "Logout", "Developer"], 60):
            return True
        else:
            # If not, click Back
            x, y = waitForText("Back", timeout=60)
            mouse.setPos(x, y)
            time.sleep(1)
            mouse.leftClick(x,y)

        time.sleep(0.05)
        if timeout and (time.time() - start) > timeout:
            return False



def main():
    # Get paths and arguments
    getTesseractPath()
    parser = argparse.ArgumentParser(description='A bot that will continue attempting to join The Isle servers until it gets in.')
    parser.add_argument('SERVER', type=str, nargs=1,
                        help='The name of the server you want to queue up')
    parser.add_argument('--sms', nargs=1, type=int,
                        help='10-digit phone number you want an SMS notification sent to when successfully connected to the server - Currently supports: Verizon, AT&T, T-Mobile, and Google Voice numbers ONLY')
    parser.add_argument('--email', nargs=1, type=str,
                        help='Email address you want a notification sent to when successfully connected to the server')

    args = parser.parse_args()
    
    # Set up notifications
    if args.sms:
        SMS = Notification("SMS", int(args.sms[0]))

    if args.email:
        EMAIL = Notification("Email", str(args.email[0]))   

    # Start the game and wait for the disclaimer
    print('Launching The Isle')
    launchGame()
    waitForText(["I understand", "EVRIMA", "Greetings"])

    # Click "I understand"
    x, y = findButtonByColor((99,168,131))
    mouse.setPos(x, y)
    time.sleep(1)
    mouse.leftClick(x,y)
    if connectionLoop(str(args.SERVER[0])):
        if args.sms:
            SMS.send()
        if args.email:
            EMAIL.send()
        print("Connected to the server! islebot is shutting down.")


if __name__ == '__main__':
    main()
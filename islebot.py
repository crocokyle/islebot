import cv2
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from pytesseract import Output
import numpy as np
from PIL import ImageGrab, ImageOps
import os
import time
from datetime import datetime
import win32api, win32con
import argparse
import pynput
import psutil
import json
from pynput.keyboard import Key, Controller


# Globals
keyboard = Controller()
coords_file = 'coordinates.json'
coords_known = False
coords_cache = {}


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


    def moveAndClick(x, y):
        mouse.setPos(x, y)
        time.sleep(1)
        mouse.leftClick(x,y)

    def moveAndDoubleClick(x, y):
        mouse.setPos(x, y)
        time.sleep(1)
        mouse.leftClick(x,y)
        time.sleep(0.05)
        mouse.leftClick(x,y)


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


def invertImage(img):
    inverted = ImageOps.invert(img)
    return inverted

def screenGrab(color=False):
    img = ImageGrab.grab()
    if not color:
        img = convertToBnW(img)
    return img


def convertToBnW(img):
    gray = img.convert('L')

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
        img = screenGrab(True)
        img = invertImage(img)
        img = convertToBnW(img)
        data = pytesseract.image_to_data(img, lang='eng', output_type=Output.DICT)
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


def waitForText(text, timeout=0, debug=False, kill=False):
    print('Waiting for text: {} timeout in {}s...'.format(text, timeout))

    if timeout:
        start = time.time()

    while True:
        img = screenGrab(True)
        img = invertImage(img)
        img = convertToBnW(img)
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
            if kill:
                # Close the game and call main()
                print("Sorry, we've run in to a problem. Islebot is starting over...")
                killTheIsle()
                main()
            else:    
                return False


def launchGame():
    os.system('start steam://rungameid/376210')


def connectionLoop(timeout=0):
    global coords_cache

    
    if timeout:
        start = time.time()

    while True: 
        # Double click the server name
        findButtonByColor((73,203,174))
        x, y = coords_cache['Server']

        mouse.moveAndClick(x, y)
        time.sleep(0.2)
        mouse.leftClick(x,y)

        # Did we connect successfully?
        if waitForText(["Herbivore", "Carnivore", "Eggs", "Humans", "SELECT" "ASSET", "Logout", "Developer"], 10):
            return True
        else:
            # If not, click Refresh
            print("Refreshing server list...")
            x, y = coords_cache['Refresh']
            mouse.moveAndDoubleClick(x, y)

        if timeout and (time.time() - start) > timeout:
            return False


def storeCoords():
    global coords_known
    with open(coords_file, 'w') as f:
        json.dump(coords_cache, f)
    coords_known = True


def loadCoords():
    global coords_cache
    global coords_known
    with open(coords_file) as f:
        coords_cache = json.load(f)
    coords_known = True
    print('Using coordinate cache')
    return coords_cache


def main():
    global coords_cache

    # Get paths and arguments
    getTesseractPath()
    parser = argparse.ArgumentParser(description='A bot that allows you to queue up for servers in The Isle and sends you an SMS or email notification when you\'re connected.')
    parser.add_argument('SERVER', type=str, nargs=1,
                        help='The name of the server you want to queue up')
    parser.add_argument('--sms', nargs=1, type=int,
                        help='10-digit phone number you want an SMS notification sent to when successfully connected to the server - Currently supports: Verizon, AT&T, T-Mobile, and Google Voice numbers ONLY')
    parser.add_argument('--email', nargs=1, type=str,
                        help='Email address you want a notification sent to when successfully connected to the server')
    parser.add_argument('-r', '--reset', action='store_true',
                        help='Resets all cached coordinates from OCR. Run this if your resolution has changed, etc.')

    args = parser.parse_args()
    
    # Set up notifications
    if args.sms:
        SMS = Notification("SMS", int(args.sms[0]))

    if args.email:
        EMAIL = Notification("Email", str(args.email[0]))   

    # Reset cache if needed
    if args.reset and os.path.exists(coords_file):
        os.remove(coords_file)

    # Load coordinates
    if not args.reset and os.path.exists(coords_file):
        coords_cache = loadCoords()

    # Start the game and wait for the disclaimer
    print('Launching The Isle')
    launchGame()
    waitForText(["I understand", "EVRIMA", "Greetings"])

    # Click "I understand"
    if not coords_known:
        x, y = findButtonByColor((99,168,131))
        coords_cache['I understand'] = (x, y)
    else:
        x, y = coords_cache['I understand']

    mouse.moveAndClick(x, y)

    # Click "Play"
    if not coords_known:
        x, y = findButtonByText("Play")
        coords_cache['Play'] = (x, y)
    else:
        x, y = coords_cache['Play']

    mouse.moveAndClick(x, y)    

    # Find the Filter input box
    print('Waiting for servers to load...')
    if not coords_known:
        #x, y = findButtonByColor((155,179,174))
        x, y = findButtonByText("Filter")
        coords_cache["Filter"] = (x, y)
    else:
        findButtonByColor((155,179,174)) # We still need to wait
        x, y = coords_cache['Filter']
    
    mouse.moveAndClick(x, y)

    # Enter the server name
    time.sleep(0.5)
    keyboard.type(str(args.SERVER[0]))

    # Exploratory serach for Refresh to complete coordinates cache
    if not coords_known:
        x, y = findButtonByText("Refresh")
        print("Found refresh button at {}, {}".format(x, y))
        coords_cache["Refresh"] = (x, y)
    else:
        x, y = coords_cache["Refresh"]

    # Connect to the server
    print("Analyzing search results...")
    if not coords_known:
        x, y = findButtonByColor((73,203,174)) # Find the server result
        coords_cache['Server'] = (x, y)
        storeCoords()
    else:
        x, y = coords_cache['Server']

    
    # If connected, send notifications and exit
    if connectionLoop():
        if args.sms:
            SMS.send()
        if args.email:
            EMAIL.send()
        print("Connected to the server! islebot is shutting down.")
        exit(0)
    



if __name__ == '__main__':
    main()
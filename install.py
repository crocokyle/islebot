import os
import requests


def downloadTesseract():
    print('Downloading Tesseract. Please wait...')
    url = 'https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha.20210506.exe'
    r = requests.get(url, allow_redirects=True)
    open('tesseract-ocr-w64-setup-v5.0.0-alpha.20210506.exe', 'wb').write(r.content)
    print('Please install Tesseract by following the prompts')
    os.system('tesseract-ocr-w64-setup-v5.0.0-alpha.20210506.exe')


def findTesseract():
    ProgramFiles = os.getenv('PROGRAMFILES')
    tPath = os.path.join(os.path.join(ProgramFiles, 'Tesseract-OCR'), 'tesseract.exe')

    print(tPath)

    if os.path.exists(tPath):
        return tPath


def main():
    if not os.path.exists('tesseract-ocr-w64-setup-v5.0.0-alpha.20210506.exe'):
        downloadTesseract()
    tPath = findTesseract()
    if tPath:
        file = open('tesseract_path.txt', 'w')
        file.write(tPath)
        file.close()

    os.system('pip3 install pytesseract')
    os.system('pip3 install opencv-python')
    os.system('pip3 install pynput')


if __name__ == '__main__':
    main()
# islebot
islebot currently uses Tesseract as a Neural Network OCR tool to locate buttons in the game UI. This prevents using hard-coded coordinates that would fail to run on multiple systems with varying resolutions. As a result of this, no two runs of islebot will be the same. It may take anywhere from 1 second to 60 seconds for it to locate a particular button. 

## Installation

```bash
git clone https://github.com/crocokyle/islebot.git
python3 install.py
```
- Continue following the prompts to install Tesseract on Windows

## Usage

`islebot.py [-h] [--sms SMS] [--email EMAIL] SERVER`


`python islebot.py --help`


### Example
- Enter the SERVER in a way that provides only one search result
```bash
python3 islebot.py --sms 8005551234 --email me@mydomain.com Zoo
```

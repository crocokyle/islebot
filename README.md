# islebot
islebot currently uses Tesseract as a Neural Network OCR tool to locate buttons in the game UI. This prevents using hard-coded coordinates that would fail to run on multiple systems with varying resolutions. During the first run of islebot, it will locate the UI elements it needs to interact with and cache them for subsequent runs. 

## Installation

[Download the latest release](https://github.com/crocokyle/islebot/releases)

`python3 install.py` 

## Usage

`islebot.py [-h] [--sms SMS] [--email EMAIL] SERVER`


`python islebot.py --help`


### Example
- Enter the SERVER in a way that provides only one search result
```bash
python3 islebot.py --sms 8005551234 --email me@mydomain.com Zoo
```

## Troubleshooting

If islebot is clicking the wrong areas or doing something it shouldn't, try resetting the coordinates cache by running with the `--reset` flag or by deleting the `coordinates.json` file in the script directory.

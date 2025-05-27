# LexiConquorer
This README provides a detailed list of instructions on how to set up the XYZ Table and the digital code environment to start and use LexiConquorer.

## Physical Setup
The first step is to setup the XYZ Table, so that the software can correctly control all the components. \
The material that is provided include some important components: 
- XYZ Table (2 servos attached)
- Power Supply
- Arduino Uno with CNC Shield (GRBL pre-installed)
- USB-A to USB Cable
- Separate arm with servo
- 3 wires to attach the CNC shield to the servos

Components you have to provide yourself:
- Conducting pen with rubber tip
- Phone (with NYT Games app)
- Cable to connect phone to device running the software
- Item of around 3-4 cm in width on which the phone can be put (should be just enough space to fit the phone on top and the arm still being able to move over it)

Underneath, a set of instructions is provided:
1) Put the XYZ Table down on a table
2) Connect the separate arm (z axis arm) with servo to the XYZ Table (can be clicked on as a puzzle piece), pen holder should be oriented to the left
3) Connect the conducting pen on the separate attached arm (screwdriver is provided)
4) Put the power supply with Arduino Uno with CNC Shield (they are connected) next to the XYZ Table
5) Attach the 3 provided wires to the CNC Shield and the separate servos (for pictures, see the report)
   - X should be connected to the long side (should be vertical side)
   - Y should be connected to the short side (should be horizontal side)
   - Z should be connected to the separately connected arm
9) Move the position of the separate arm to the left bottom (for pictures, see the report)
10) Place down the item of around 3-4 cm in height left of the vertical arm and above the horizontal arm
11) Place the phone on top of the item
12) Connect the USB-A to USB cable to the Arduino Uno and the device on which the software will run
13) Connect the phone to the device as well (make sure data transfer and USB debugging is turned on)
14) Open the NYT Games app on the phone and start either the Spelling Bee or the Wordle

The physical setup is now completed!

## Digital Setup
Now that the physical environment is set up, it is time to set up the digital environment. Prerequisites:
- Python >=3.8 is installed
- You are running a Unix-based system. These instructions do not apply to Windows and are only tested on MacOS. They should also work on Linux machines with minimal changes. 
- Potentially: have a OpenAI API Key with credit

The instructions to set up the digital environment:
1) Download and open the submission files
2) Open a Terminal and locate to the /LexiConquorer folder
3) Run `python3 -m venv venv` to create a virtual environment and `source venv/bin/activate` to enter it.
4) Install the required packages by running `pip3 install -r requirements.txt`
5) Install `adb` using the following link: https://developer.android.com/tools/releases/platform-tools
6) Install `scrcpy` using the following link: https://github.com/Genymobile/scrcpy?tab=readme-ov-file (`brew install scrcpy` for MacOS) 
7) Open a new Terminal and run `scrcpy` (the screen of the phone you connected should now pop up) (this Terminal cannot be used as long as `strcpy` runs)
8) Change back to the other Terminal. Run one of the calibration scripts by performing `python3 Calibration/*Calib.py` (where * is the game)
   - Make sure the robot is correctly calibrated before performing the next steps!
9) Run the following command to export an OpenAI key (one is provided, but may not be valid anymore at time of execution): `export OPENAI_API_KEY=[KEY]`, KEY is provided in key.txt in the submission.
10) For all code files, make sure the port is correctly set to the USB port in your device to which the Arduino is connected.
11) In `TheLexiConquorer.py`, set the `CHATGPTTOGGLE` of both games to `False` (classical approach) or `True` (ChatGPT API implementation)
12) Are you playing the Spelling Bee?
    - Set the correct letters in the right order in `TheLexiConquorer.py`
13) Run LexiConquorer with the corresponding game as following: `sudo -E env PATH=${PATH} OPENAI_API_KEY=$OPENAI_API_KEY python3 TheLexiConquerer.py [game]`, where `[game]` is either `1` (Spelling Bee) or `2` (Wordle)
    - Are you running into package issues? Install the packages globally (you may want to use a VM)

The robot should now start moving and solve the provided puzzle!

## Troubleshooting:
- Is the robot moving into the wrong direction? Then the servos direction need to be changed.
  - Change the direction of the corresponding servos by opening Arduino IDE, opening the Serial Monitor (Arduino must be connected to laptop). Type `$$` to see current settings. Change `$3` to the needed value.


Are you running into any issues? Be sure to get in touch with us to see if we can help.



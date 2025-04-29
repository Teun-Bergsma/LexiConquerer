#!/bin/bash

echo "Start Calibration Process"
sudo python3 spellingBeeCalib.py

echo "Start Spelling Bee"
sudo python3 TheLexiConquerer.py 1


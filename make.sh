#!/usr/bin/env bash
rm -rf build/ dist/
pyinstaller main.py --onefile --icon=assets/amazon.ico
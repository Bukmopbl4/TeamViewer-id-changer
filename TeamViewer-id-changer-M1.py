#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import random
import re
import string
import sys

print('''
--------------------------------
Tested on:
TeamViewer 15.33.7 ID Changer
for MAC OS Intel/M1
Python 3.10.4 
Version: 0.3 2022
--------------------------------
''')

if platform.system() != "Darwin":
    print("This script can be run only on MAC OS.")
    sys.exit()

if os.geteuid() != 0:
    print("This script must be run form root.")
    sys.exit()

if "SUDO_USER" in os.environ:
    USERNAME = os.environ["SUDO_USER"]
    if USERNAME == "root":
        print("Can not find user name. Run this script via sudo from regular user")
        sys.exit()
else:
    print("Can not find user name. Run this script via sudo from regular user")
    sys.exit()

HOMEDIRLIB = f"/Users/{USERNAME}/library/preferences/"
GLOBALLIB = "/library/preferences/"

CONFIGS = []


# Find config files
def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

for file in listdir_fullpath(HOMEDIRLIB):
    if 'teamviewer' in file.lower():
        CONFIGS.append(file)

for file in listdir_fullpath(GLOBALLIB):
    if 'teamviewer' in file.lower():
        CONFIGS.append(file)

if not CONFIGS:
    print('''
    There is no TemViewer configs found.
    Maybe you have deleted it manualy or never run TeamViewer after installation.
    Nothing to delete.
    ''')
else:
    # Delete config files
    print("Configs found:\n")
    for file in CONFIGS: print(file)
    print('''
This files will be DELETED permanently.
All TeamViewer settings will be lost
''')
    input("Press Enter to continue or CTR+C to abort...")

    for file in CONFIGS:
        try:
            os.remove(file)
        except:
            print("Cannot delete config files. Permission denied?")
            sys.exit()
    print("Done.")

# Find binaryes

TMBINARYES = [
    '/Applications/TeamViewer.app/Contents/MacOS/TeamViewer',
    '/Applications/TeamViewer.app/Contents/MacOS/TeamViewer_Service',
    '/Applications/TeamViewer.app/Contents/MacOS/TeamViewer_Desktop_Proxy',
    '/Applications/TeamViewer.app/Contents/Helpers/Restarter',
    '/Applications/TeamViewer.app/Contents/Helpers/TeamViewer_Assignment'
]

for file in TMBINARYES:
    if os.path.exists(file):
        pass
    else:
        print(f"File not found: {file}")
        print("Install TeamViewer correctly")
        sys.exit()


# Patch files

def idpatch(fpath, platf, serial):
    file = open(fpath, 'r+b')
    binary = file.read()
    PlatformPattern = "IOPlatformExpert.{6}"
    SerialPattern = "IOPlatformSerialNumber%s%s%s"

    binary = re.sub(bytes(PlatformPattern, 'utf-8'), bytes(platf, 'utf-8'), binary)
    formattedSerialPattern = SerialPattern % ('\x00', "[0-9a-zA-Z]{8,8}", '\x00')
    formattedSerial = SerialPattern % ('\x00', serial, '\x00')
    binary = re.sub(bytes(formattedSerialPattern, 'utf-8'), bytes(formattedSerial, 'utf-8'), binary)

    file = open(fpath, 'wb').write(binary)
    return True


def random_generator(size=8, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


RANDOMSERIAL = random_generator(8)
RANDOMPLATFORM = "IOPlatformExpert" + random_generator(6)

for file in TMBINARYES:
    try:
        idpatch(file, RANDOMPLATFORM, RANDOMSERIAL)
    except Exception as e:
        print(f"Error: can not patch file {file} [{e}]")
        sys.exit()

print("PlatformDevice: " + RANDOMPLATFORM)
print("PlatformSerial: " + RANDOMSERIAL)

try:
    os.system("sudo killall TeamViewer")
except:
    print("Cannot kill TeamViewer")
    sys.exit()
print("TeamViewer process was killed.")

os.system("sudo codesign --force --deep --sign - /Applications/TeamViewer.app/Contents/MacOS/TeamViewer")

print('''
ID changed sucessfully.
!!!No need to Restart your computer!!!!
''')
# VOXL ESC Tools
VOXL ESC Tools is a Python software package which allows testing, calibration and diagnostics of ESCs using a PC. Note that a compatible ESC from ModalAi is required.

## Hardware Requirements
- Compatible ESC (see [docs](https://docs.modalai.com/modal-escs/) )
- USB-to-serial adapter (3.3V signals) with a 6-pin Hirose DF13 connector (see [docs](https://docs.modalai.com/modal-esc-v2-manual/) for pin-out)
 - use UART1 pins on the ESC V2 (UART2 is reserved for future use)
 - the device should appear as /dev/ttyUSBx on Linux machines and /dev/cu.usbserial-* on OSX
- Fixed or adjustable power supply (check ESC data sheet for acceptable voltage), rated for at least several Amps (depending on tests being performed). Note that insufficient current capacity of the power supply may cause ESC reset or other undesired behavior.

## Software Compatibility
- The ESC Tools have been tested using Python 2.7

## Accessing the Esc Tools Software
- The ESC tools consist of two parts:
 - voxl-esc-tools-bin : proprietary software (voxl-esc-tools-bin-x.x.x.zip) : [download link](https://developer.modalai.com/asset)
 - voxl-esc-tools : (this repository)
- After downloading voxl-esc-tools-bin zip file, unzip it in the current directory (voxl-esc/tools), which will place the contents into existing voxl-esc/tools/voxl-esc-tools-bin directory
```
cp voxl-esc-tools-bin-x.x.x.zip voxl-esc/tools/
cd voxl-esc/tools
unzip voxl-esc-tools-bin-x.x.x.zip
```

## Other Software Prerequisites
### Installation Instructions for Ubuntu 16.04

```
#add yourself to group dialout so that you can access serial ports
#(need to log out and log back in after adding to group)
sudo addgroup <your_user_name> dialout

sudo apt-get update
sudo apt-get -y install apt-utils software-properties-common python-pip python-setuptools
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade numpy pyserial
```
### Installation Instructions for OSX
```
sudo easy_install pip
sudo -H pip install --upgrade pip
sudo -H pip install --upgrade numpy pyserial
```

## Usage Examples

### Scanning for ESCs
- the script opens all possible serial ports and scans for ESCs on different baud rates
- if ESC(s) are found, the script receives their ID, Software and Hardware versions
 - Hardware version is board-specific and cannot be changed
 - Firmware version is the version of the ESC Firmware
```
python voxl-esc-scan.py
Scanning for ESC firmware: /dev/cu.usbserial-A7027C8E, baud: 250000

ESC(s) detected on port: /dev/cu.usbserial-A7027C8E using baudrate: 250000
Attempting to open...
Detected ESCs With Firmware:
---------------------
ID: 0, SW: 31, HW: 30 (ModalAi 4-in-1 ESC V2 RevA)
ID: 1, SW: 31, HW: 30 (ModalAi 4-in-1 ESC V2 RevA)
ID: 2, SW: 31, HW: 30 (ModalAi 4-in-1 ESC V2 RevA)
ID: 3, SW: 31, HW: 30 (ModalAi 4-in-1 ESC V2 RevA)
```

### Uploading Parameters
```
python voxl-esc-upload-params.py --params-file ../params/esc_params_modalai_4_in_1.xml
Scanning for ESC firmware: /dev/cu.usbserial-A7027C8E, baud: 250000

ESC(s) detected on port: /dev/cu.usbserial-A7027C8E using baudrate: 250000
Attempting to open...
ESCs detected:
---------------------
ID: 0, SW: 31, HW: 30
ID: 1, SW: 31, HW: 30
ID: 2, SW: 31, HW: 30
ID: 3, SW: 31, HW: 30
---------------------
Loading XML config file...
Uploading params...
-- board config
-- id config
-- uart config
-- tune config
    DONE
Resetting...
    DONE
```

### Spinning Motors
- if ID 255 is specified, all detected ESCs will be commanded to spin, otherwise just the single specified ID
- be very careful when specifying desired power or rpm (start with low power like 10, if unsure)
- you will be prompted to type "yes" before motors will spin (for safety)
```
python voxl-esc-spin.py --id 0 --power 10
python voxl-esc-spin.py --id 255 --power 10
python voxl-esc-spin.py --id 0 --rpm 3000
```

```
python voxl-esc-spin.py --id 255 --power 10
Scanning for ESC firmware: /dev/cu.usbserial-A7027C8E, baud: 250000

ESC(s) detected on port: /dev/cu.usbserial-A7027C8E using baudrate: 250000
Attempting to open...
WARNING:
This test requires motors to spin at high speeds with
propellers attached. Please ensure that appropriate
protective equipment is being worn at all times and
that the motor and propeller are adequately isolated
from all persons.

For best results, please perform this test at the
nominal voltage for the battery used.

Type "Yes" to continue: yes
[0] RPM: 0, PWR: 0, VBAT: 12.13V, TEMPERATURE: 39.09C, CURRENT: 0.02A
[1] RPM: 0, PWR: 0, VBAT: 12.16V, TEMPERATURE: 39.89C, CURRENT: 0.00A
[2] RPM: 0, PWR: 0, VBAT: 12.18V, TEMPERATURE: 39.81C, CURRENT: 0.01A
[3] RPM: 0, PWR: 0, VBAT: 12.18V, TEMPERATURE: 39.54C, CURRENT: 0.00A
[0] RPM: 0, PWR: 0, VBAT: 12.13V, TEMPERATURE: 39.09C, CURRENT: 0.02A
[1] RPM: 0, PWR: 0, VBAT: 12.16V, TEMPERATURE: 39.89C, CURRENT: 0.00A
[2] RPM: 0, PWR: 0, VBAT: 12.18V, TEMPERATURE: 39.81C, CURRENT: 0.01A
[3] RPM: 0, PWR: 0, VBAT: 12.18V, TEMPERATURE: 39.54C, CURRENT: 0.00A
...
...
[0] RPM: 5229, PWR: 10, VBAT: 12.12V, TEMPERATURE: 39.03C, CURRENT: 0.06A
[1] RPM: 5226, PWR: 10, VBAT: 12.14V, TEMPERATURE: 39.80C, CURRENT: 0.06A
[2] RPM: 5242, PWR: 10, VBAT: 12.15V, TEMPERATURE: 39.70C, CURRENT: 0.10A
[3] RPM: 5279, PWR: 10, VBAT: 12.15V, TEMPERATURE: 39.31C, CURRENT: 0.05A
[0] RPM: 5239, PWR: 10, VBAT: 12.11V, TEMPERATURE: 38.94C, CURRENT: 0.03A
[1] RPM: 5226, PWR: 10, VBAT: 12.14V, TEMPERATURE: 39.80C, CURRENT: 0.06A
[2] RPM: 5242, PWR: 10, VBAT: 12.15V, TEMPERATURE: 39.70C, CURRENT: 0.10A
[3] RPM: 5277, PWR: 10, VBAT: 12.15V, TEMPERATURE: 39.37C, CURRENT: 0.11A
...
```

## ESC Parameters

Some ESC parameter examples are maintained in this repository in *params* directory. See the XML parameter files for details and additional documentation

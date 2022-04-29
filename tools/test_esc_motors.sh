#!/bin/bash

DIR="/home/projects/voxl-esc/tools"

DEVICE="/dev/ttyUSB0"
BAUD="250000"
POWER="10"
TIMEOUT="5"

#Go to voxl-esc tools directory
cd $DIR/tools/

#use Python 2.7.xx
for mot in {0..3}
do
   python voxl-esc-spin.py --device $DEVICE --baud-rate $BAUD --id $mot --power $POWER --timeout $TIMEOUT --skip-prompt True
done
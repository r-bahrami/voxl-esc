#!/bin/bash


DEVICE="/dev/ttyUSB0"
BAUD="250000"
POWER="10"
TIMEOUT="5"


echo "--- voxl esc spin helper ---"
echo "WARNING: All motors will SPIN." 
echo "Please remove all propellers, then press ANY key to proceed . . . "

#wait here
read

#use Python 2.7.xx
for mot in {0..3}
do
   python voxl-esc-spin.py --device $DEVICE --baud-rate $BAUD --id $mot --power $POWER --timeout $TIMEOUT --skip-prompt True
done

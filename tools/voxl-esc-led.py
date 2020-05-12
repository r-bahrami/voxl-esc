# Copyright (c) 2020 ModalAI Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# 4. The Software is used solely in conjunction with devices provided by
#    ModalAI Inc.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# For a license to use on non-ModalAI hardware, please contact license@modalai.com

import sys
sys.path.append('./voxl-esc-tools-bin')

from libesc import *
import time
import argparse

parser = argparse.ArgumentParser(description='ESC LED Test Script')
parser.add_argument('--device',                 required=False, default=None)
parser.add_argument('--baud-rate',              required=False, default=None)
args = parser.parse_args()

devpath  = args.device
baudrate = args.baud_rate

if devpath is None:
    scanner = SerialScanner()
    (devpath, baudrate) = scanner.scan()

    if devpath is not None and baudrate is not None:
        print ''
        print 'ESC(s) detected on port: ' + devpath + ' using baudrate: ' + str(baudrate)
        print 'Attempting to open...'
    else:
        print 'No ESC(s) detected, exiting.'
        sys.exit(1)

# create ESC manager and search for ESCs
manager = EscManager()
manager.open(devpath, baudrate)

# wait a little to let manager find all ESCs
time.sleep(1)
num_escs = len(manager.get_escs())
if num_escs < 1:
    print 'No ESCs detected--exiting.'
    sys.exit(0)

escs = manager.get_escs()

print 'Running LED Test...'
update_cntr = 0
t_start = time.time()
#while time.time() - t_start < timeout:
while True:
    time.sleep(0.01)
    update_cntr += 1

    #cycle through red, green, blue
    dt = (time.time() - t_start) % 3.0
    led_red   = 1 if  dt<1           else 0
    led_green = 1 if (dt>1 and dt<2) else 0
    led_blue  = 1 if (dt>2)          else 0

    for esc in escs:
        esc.set_target_power(0)
        esc.set_leds([led_red, led_green, led_blue])  #0 or 1 for R G and B values.. binary for now

    manager.send_pwm_targets()  #led colors are sent along the power commands in the same packet
    #note that status LED will also blink, since it blinks when ESC receives commands

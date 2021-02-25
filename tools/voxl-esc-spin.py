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
from esc_scanner import EscScanner
import time
import numpy as np
import argparse


parser = argparse.ArgumentParser(description='ESC Test Spin Script')
parser.add_argument('--device',                 required=False, default=None)
parser.add_argument('--baud-rate',              required=False, default=None)
parser.add_argument('--id',          type=int,  required=True,  default=0)
parser.add_argument('--power',       type=int,  required=False, default=10)
parser.add_argument('--rpm',         type=int,  required=False, default=None)
parser.add_argument('--timeout',     type=int,  required=False, default=0)
parser.add_argument('--skip-prompt', type=str,  required=False, default='False')
parser.add_argument('--led-red',     type=int,  required=False, default=0)
parser.add_argument('--led-green',   type=int,  required=False, default=0)
parser.add_argument('--led-blue',    type=int,  required=False, default=0)
parser.add_argument('--cmd-rate',    type=int,  required=False, default=100)
args = parser.parse_args()

devpath  = args.device
baudrate = args.baud_rate
esc_id   = args.id
spin_pwr = args.power #0-100
spin_rpm = args.rpm #0-30000 .. limited to 30K for safety
timeout  = args.timeout
led_red  = int(args.led_red > 0)
led_green= int(args.led_green > 0)
led_blue = int(args.led_blue > 0)
cmd_rate = args.cmd_rate

MAX_SAFE_RPM = 30000

#optionally skip the safety prompt that asks to enter "yes" before spinning
skip_prompt = 'True' in args.skip_prompt or 'true' in args.skip_prompt

if spin_pwr < -100 or spin_pwr > 100:
    print('ERROR: Spin power must be between -100 and 100')
    sys.exit(1)

if spin_rpm is not None and (spin_rpm < -MAX_SAFE_RPM or spin_rpm > MAX_SAFE_RPM):
    print('ERROR: Spin rpm must be between %d and %d' % (-MAX_SAFE_RPM,MAX_SAFE_RPM))
    sys.exit(1)

if timeout < 0:
    print('ERROR: Timeout should be non-negative value of seconds')
    sys.exit(1)

if cmd_rate < 10:
    print('ERROR: Command rate is too low, the ESC will timeout')
    sys.exit(1)

# quick scan for ESCs to detect the port
scanner = EscScanner()
(devpath, baudrate) = scanner.scan(devpath, baudrate)

if devpath is not None and baudrate is not None:
    print('INFO: ESC(s) detected on port: ' + devpath + ', baud rate: ' + str(baudrate))
else:
    print('ERROR: No ESC(s) detected, exiting.')
    sys.exit(1)


# create ESC manager and search for ESCs
try:
    esc_manager = EscManager()
    esc_manager.open(devpath, baudrate)
except Exception as e:
    print('ERROR: Unable to connect to ESCs :')
    print e
    sys.exit(1)

# wait a little to let manager find all ESCs
time.sleep(0.25)
num_escs = len(esc_manager.get_escs())
if num_escs < 1:
    print('ERROR: No ESCs detected--exiting.')
    sys.exit(1)

escs = []
if esc_id != 255:
    esc = esc_manager.get_esc_by_id(esc_id)
    if esc is None:
        print('ERROR: Specified ESC ID not found--exiting.')
        sys.exit(1)
    escs.append(esc)
else:
    escs = esc_manager.get_escs()

# warn user
if not skip_prompt:
    print('WARNING: ')
    print('This test requires motors to spin at high speeds with')
    print('propellers attached. Please ensure that appropriate')
    print('protective equipment is being worn at all times and')
    print('that the motor and propeller are adequately isolated')
    print('from all persons.')
    print('')
    print('For best results, please perform this test at the')
    print('nominal voltage for the battery used.')
    print('')
    response = raw_input('Type "Yes" to continue: ')
    if response not in ['yes', 'Yes', 'YES']:
        print('Test canceled by user')
        sys.exit(1)

# spin up
if esc_id != 255:
    esc_manager.set_highspeed_fb(esc_id)  #tell ESC manager to only request feedback from this ID (so we get feedback 4x more often)

for esc in escs:
    esc.set_leds([led_red, led_green, led_blue])  #0 or 1 for R G and B values.. binary for now

t_start = time.time()
update_cntr = 0
while timeout == 0 or time.time() - t_start < timeout:
    update_cntr += 1
    time.sleep(1.0/cmd_rate)

    if spin_rpm is not None:
        for esc in escs:
            esc.set_target_rpm(spin_rpm)
        esc_manager.send_rpm_targets()
    else:
        for esc in escs:
            esc.set_target_power(spin_pwr)
        esc_manager.send_pwm_targets()

    for esc in escs:
        print('[%d] RPM: %.0f, PWR: %.0f, VBAT: %.2fV, TEMPERATURE: %.2fC, CURRENT: %.2fA' % (esc.get_id(), esc.get_rpm(), esc.get_power(), esc.get_voltage(), esc.get_temperature(), esc.get_current()))

print('Finished!')

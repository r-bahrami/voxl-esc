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

#from libesc.escmanager import EscManager
from libesc import *
from esc_scanner import EscScanner
import time
import numpy as np
from libesc.esctypes import EscTypes as types

import argparse

parser = argparse.ArgumentParser(description='ESC Upload Firmware Script')
parser.add_argument('--device',               required=False, default=None)
parser.add_argument('--firmware-baud-rate',   required=False, default=None)
parser.add_argument('--bootloader-baud-rate', type=int, required=False, default=230400)
parser.add_argument('--firmware-file',        type=str, required=True,  default="")
parser.add_argument('--id',                   type=int, required=True,  default=0)
parser.add_argument('--skip-firmware-reset',  type=str, required=False, default="false")
parser.add_argument('--progress-bar-type',    type=str, required=False, default="fancy")
args = parser.parse_args()

devpath              = args.device
firmware_baud_rate   = args.firmware_baud_rate
bootloader_baud_rate = args.bootloader_baud_rate
firmware_file        = args.firmware_file
esc_id               = args.id

# load file
f = open(firmware_file, "rb")
firmware_binary = []
try:
    byte = f.read(1)
    while byte != "":
        firmware_binary.append(ord(byte))
        byte = f.read(1)
except:
    print('ERROR: Unable to open firmware file %s' % (firmware_file))
    sys.exit(1)
finally:
    f.close()

esc_manager = EscManager()

if "true" not in args.skip_firmware_reset.lower():
    # quick scan for ESCs to detect the port
    scanner = EscScanner()
    (devpath, firmware_baud_rate) = scanner.scan(devpath, firmware_baud_rate)

    if devpath is not None and firmware_baud_rate is not None:
        print('INFO: ESC(s) detected on port: ' + devpath + ', baud rate: ' + str(firmware_baud_rate))
    else:
        print('ERROR: No ESC(s) detected, exiting.')
        sys.exit(1)

    # reset the required ESC so that it can enter bootloader
    if firmware_baud_rate is not None:
        try:
            esc_manager.open(devpath, firmware_baud_rate)
            time.sleep(0.25)
            escs = esc_manager.get_escs()
            esc_ids = [e.get_id() for e in escs]
            if not esc_id in esc_ids:
                print('WARNING: Specified ESC ID not detected; perform manual power cycle now')
            else:
                print('INFO: Sending reset command to ESC ID %d' % esc_id)
                esc_manager.reset_id(esc_id)
                time.sleep(0.25)
        except Exception as e:
            print('WARNING: Unable to detect ESCs in order to reset them..:')
            print(e)
            print('WARGING: Attempting to continue')

            #since we did not find ESCs with firmware, we can't send the reset message
            #so, just try to establish communication with bootloader
            esc_manager.open(devpath, bootloader_baud_rate)

else:
    esc_manager.open(devpath, bootloader_baud_rate)


# switch to bootloader protocol
esc_manager.set_protocol(types.ESC_PROTOCOL_BOOTLOADER)
esc_manager.set_baudrate(bootloader_baud_rate)

print('INFO: Installing firmware to ESC ID %d : %s' % (esc_id,firmware_file))
print('')
progress_bar_length = 50
if args.progress_bar_type == 'simple':
    simple_progress_bar_current_length = 0
    print('\tProgress:  0' + '.'*(progress_bar_length-5) + '100')
    print('\t          '),


for progress in esc_manager.upload_firmware(firmware_binary, esc_id):
    if progress == -1:
        print('ERROR: An error occured during the write process.')
        sys.exit(1)
    else:
        if args.progress_bar_type == 'fancy':
            bar_completed_length = int(progress_bar_length*progress)
            progress_bar = '#' * bar_completed_length + ' ' * (progress_bar_length-bar_completed_length)
            print('\033[F\tProgress: %3d%% [%s]' % ((100 * progress),progress_bar))
        elif args.progress_bar_type == 'simple':
            bar_completed_length = int(progress_bar_length/2*progress)
            if bar_completed_length > simple_progress_bar_current_length:
                print('#'),
                sys.stdout.flush()
                simple_progress_bar_current_length += 1


esc_manager.close()
print('')
print('INFO: Firmware successfully updated for ESC id %d' % (esc_id))

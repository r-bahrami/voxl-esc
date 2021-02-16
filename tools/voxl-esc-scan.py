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
from esc_boards import *
import argparse

parser = argparse.ArgumentParser(description='ESC Scan Script')
parser.add_argument('--device',                 required=False, default=None)
parser.add_argument('--baud-rate',              required=False, default=None)
args = parser.parse_args()

devpath  = args.device
baudrate = args.baud_rate
protocol = 'None'

scanner = EscScanner()
(devpath, baudrate) = scanner.scan(devpath, baudrate)

if devpath is not None and baudrate is not None:
    protocol = scanner.get_protocol()
    print('INFO: ESC(s) detected on port: ' + devpath + ', baud rate: ' + str(baudrate))
    print('INFO: Detected protocol: ' + protocol)
else:
    print('ERROR: No ESC(s) detected, exiting.')
    sys.exit(1)

try:
    esc_manager = EscManager()
    esc_manager.open(devpath, baudrate)
except Exception as e:
    print('ERROR: Unable to connect to ESCs :')
    print e
    sys.exit(1)

# wait a little to let manager find all ESCs
time.sleep(0.25)

print('INFO: Additional Information:')
print('INFO: ---------------------')
time.sleep(0.1)
for e in esc_manager.get_escs():
    versions      = e.get_versions()
    uid           = e.get_uid()
    fw_git_hash   = e.get_sw_git_hash()
    boot_git_hash = e.get_boot_git_hash()
    boot_version  = e.get_boot_version()
    hardware_name = get_esc_board_description(versions[1])

    print('\tID         : %d' % (e.get_id()))
    print('\tBoard      : version %d: %s' % (versions[1],hardware_name))
    print('\tUID        :'),
    print('0x{}'.format(''.join(hex(x).lstrip("0x") for x in uid[::-1])))
    print('\tFirmware   : version %4d, hash %s' % (versions[0],fw_git_hash))
    print('\tBootloader : version %4d, hash %s' % (boot_version, boot_git_hash))
    print('')
print('---------------------')

esc_manager.close()

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
import argparse

parser = argparse.ArgumentParser(description='ESC Params Verification Script')
parser.add_argument('--device',        required=False, default=None)
parser.add_argument('--baud-rate',     required=False, default=None)
parser.add_argument('--num-escs',      type=int, required=False,  default=4)
parser.add_argument('--save-params',   type=int, required=False,  default=0)
args = parser.parse_args()

devpath     = args.device
baudrate    = args.baud_rate
num_escs    = args.num_escs
save_params = args.save_params

# quick scan for ESCs to detect the port
scanner = EscScanner()
(devpath, baudrate) = scanner.scan(devpath, baudrate)

if devpath is not None and baudrate is not None:
    print('INFO: ESC(s) detected on port: ' + devpath + ', baud rate: ' + str(baudrate))
else:
    print('ERROR: No ESC(s) detected, exiting.')
    sys.exit(1)

try:
    esc_manager = EscManager()
    esc_manager.open(devpath, baudrate)
except Exception as e:
    print 'ERROR: Unable to open serial port :'
    print e
    sys.exit(1)

# wait a little to let manager find all ESCs and get info
time.sleep(0.25)

escs = esc_manager.get_escs()
esc_ids = [e.get_id() for e in escs]

num_invalid_params = 0

# send request for each ESC to send back its params
for esc_id in range(num_escs):
    if esc_id not in esc_ids:
        print 'ERROR: ESC ID %d not found' % (esc_id)
        continue

    esc = esc_manager.get_esc_by_id(esc_id)
    esc_manager.request_config_id(esc_id)
    esc_manager.request_config_board(esc_id)
    esc_manager.request_config_uart(esc_id)
    esc_manager.request_config_tune(esc_id)

    # wait for the params responses to come back
    time.sleep(0.1)

    if not esc.params.is_valid():
        print 'ERROR: Params for ID %d are invalid!' % (esc_id)
        num_invalid_params +=1
    else:
        # get the params as XML string and save to a file
        params_str = esc.params.get_xml_string()

        # try to find a match with existing xml file in params directory
        params_candidates = glob.glob('../params/*.xml')
        for param_file in params_candidates:
            with open(param_file, 'r') as f:
                temp_param_str = f.read()
            try_params = params_from_xml(temp_param_str)
            if try_params.get_param_bytes_all() == esc.params.get_param_bytes_all():
                print 'INFO: Params from ID %d match %s' % (esc_id,param_file)

        if save_params:
            xml_out_file = 'esc%d_params.xml' % (esc_id)
            with open(xml_out_file , 'w') as f:
                f.write(params_str)
                print 'INFO: Saved params from ESC ID %d to %s' %(esc_id, xml_out_file)

#compare all params from all ESCs
num_params_match = 0;
for esc_id in esc_ids:
    if esc_manager.get_esc_by_id(esc_ids[0]).params.get_param_bytes_all() != \
        esc_manager.get_esc_by_id(esc_id).params.get_param_bytes_all():
        print 'ERROR: Params from ID %d and %d are not the same' % (esc_ids[0],esc_id)
    else:
        num_params_match += 1

if num_escs == len(esc_ids) and num_params_match == num_escs and num_invalid_params == 0:
    print 'INFO: Success! Params in all ESCs are valid and identical.'
else:
    print 'ERROR: Some params are invalid or not the same!'
    print '       Number of ESCs expected     : %d' % num_escs
    print '       Number of ESCs found        : %d' % (len(esc_ids))
    print '       Number of invalid params    : %d' % (num_invalid_params)
    print '       Number of matched params    : %d' % (num_params_match)

esc_manager.close()

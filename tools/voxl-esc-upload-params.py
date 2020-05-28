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
from libesc.esctypes import EscTypes as types
import time
import argparse

parser = argparse.ArgumentParser(description='ESC Upload Parameters Script')
parser.add_argument('--device',              required=False, default=None)
parser.add_argument('--baud-rate',           required=False, default=None)
parser.add_argument('--params-file',         type=str, required=True,  default="")
parser.add_argument('--params-filter',       type=str, required=False, default="all")
args = parser.parse_args()

devpath       = args.device
baudrate      = args.baud_rate
params_file   = args.params_file
params_filter = args.params_filter

if devpath is not None and baudrate is None:
    print 'ERROR: Please provide baud rate with --baud-rate option'
    sys.exit(1)

if devpath is None:
    print 'INFO: Device and baud rate are not provided, attempting to autodetect..'
    scanner = SerialScanner()
    (devpath, baudrate) = scanner.scan()

    if devpath is not None and baudrate is not None:
        print ''
        print 'INFO: ESC(s) detected on port: ' + devpath + ' using baudrate: ' + str(baudrate)
        print 'INFO: Attempting to open...'
    else:
        print 'ERROR: No ESC(s) detected, exiting.'
        sys.exit(1)

# create ESC manager and search for ESCs
try:
    esc_manager = EscManager()
    esc_manager.open(devpath, baudrate)
except Exception as e:
    print 'ERROR: Unable to connect to ESCs :'
    print e
    sys.exit(1)

time.sleep(0.25)
escs = esc_manager.get_escs()
esc_ids = [e.get_id() for e in escs]
if len(escs) == 0:
    print 'ERROR: No ESCs detected, exiting.'
    esc_manager.close()
    sys.exit(0)
print 'INFO: ESCs detected:'
print 'INFO: ---------------------'

for e in esc_manager.get_escs():
    versions = e.get_versions()
    print 'ID: %d, SW: %d, HW: %d' % (e.get_id(), versions[0], versions[1])
print '---------------------'

esc = esc_manager.esc_dummy

# check for .xml or .eep (binary) config files
filename, file_extension = os.path.splitext(params_file)
if os.path.isfile(params_file) and file_extension == '.xml':
    print 'INFO: Loading XML config file...'
    with open(params_file, 'r') as file:
        xml_string = file.read()
        esc.params.parse_xml_string( xml_string )

elif os.path.isfile(params_file) and file_extension == '.eep':
    print 'INFO: Loading EEP config file...'
    with open(params_file, 'rb') as file:
        param_bytes = file.read()
        esc.params.parse_params_all( param_bytes )
else:
    print 'ERROR: Unsupported file type, exiting.'
    esc_manager.close()
    sys.exit(1)

print 'INFO: Uploading params...'

if 'all' in params_filter or 'board' in params_filter:
    print '-- board config'
    esc_manager.push_config_data(types.ESC_PACKET_TYPE_BOARD_CONFIG)
    time.sleep(0.1)

if 'all' in params_filter or 'id' in params_filter:
    print '-- id config'
    esc_manager.push_config_data(types.ESC_PACKET_TYPE_ID_CONFIG)
    time.sleep(0.1)

if 'all' in params_filter or 'uart' in params_filter:
    print '-- uart config'
    esc_manager.push_config_data(types.ESC_PACKET_TYPE_UART_CONFIG)
    time.sleep(0.1)

if 'all' in params_filter or 'tune' in params_filter:
    print '-- tune config'
    esc_manager.push_config_data(types.ESC_PACKET_TYPE_TUNE_CONFIG)
    time.sleep(0.1)

print '    DONE'
# sleep before final reset
time.sleep(1)
# reset all ESCs
print 'INFO: Resetting ESCs...'
esc_manager.reset_all()
print '    DONE'
esc_manager.close()

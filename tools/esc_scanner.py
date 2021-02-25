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

import os
import platform
import subprocess
from libesc import *
from libesc.escmanager import *

class EscScanner:
    system               = None
    port_candidates      = []
    firmware_baudrates   = (250000, 921600, 230400, 57600, 115200, 2000000, 6000000)
    bootloader_baudrates = (38400, 230400)
    is_voxl              = False
    uart_port_desc       = ['uart','serial','vcp','ttl232','stlink']
    protocol_type        = None

    def __init__(self):
        self.system = None

    def detect_voxl(self):
        try:
            voxl_version_info = subprocess.check_output(['voxl-version'])
            self.is_voxl = True
        except:
            pass

    def get_protocol(self):
        return self.protocol_type

    def scan(self, device=None, baudrate=None):
        if (baudrate is not None):
            self.firmware_baudrates = [baudrate]

        if device is None:
            self.system = platform.system()  # detect OS
            self.detect_voxl()               # detect VOXL

            if self.is_voxl:
                self.port_candidates = ['/dev/slpi-uart-7','/dev/slpi-uart-5','/dev/slpi-uart-12','/dev/slpi-uart-9']
            elif self.system == 'Windows':
                self.port_candidates = ['COM%s' % (i + 1) for i in range(100)]
            elif self.system == 'Linux' or self.system == 'Darwin':
                import serial.tools.list_ports as portlist
                self.ports = portlist.comports()
                print('INFO: All COM ports:')
                for pt in self.ports:
                    print("\t" + str(pt.device) + " : " + str(pt.description))

                    # see if any keywords in port description match
                    for desc in self.uart_port_desc:
                        if desc in pt.description.lower():
                            self.port_candidates.append(pt.device)

                print('INFO: UART Port Candidates:')
                for pt in self.port_candidates:
                    print("\t" + pt)
            else:
                raise Exception('Unsupported OS')

        else:
            self.port_candidates = [device]

        # check for ESCs in firmware application
        for port in self.port_candidates:
            for baud in self.firmware_baudrates:
                print('INFO: Scanning for ESC firmware: ' + port + ', baud: ' + str(baud))

                try:                             # try to open serial port
                    esc_manager = EscManager()
                    esc_manager.open(port, baud)
                except Exception as e:
                    print(e)
                    continue

                # request firmware version and see if there is a response
                time.sleep(0.025)
                escs = esc_manager.get_escs()

                if len(escs) > 0:
                    esc_manager.close()
                    self.protocol_type = 'firmware'
                    return (port, baud)

                esc_manager.close()

        # check for ESCs in bootloader
        for port in self.port_candidates:
            for baud in self.bootloader_baudrates:
                print('INFO: Scanning for ESC bootloader: ' + port + ', baud: ' + str(baud))

                try:                              # try to open serial port
                    esc_manager = EscManager()
                    esc_manager.open(port, baud)
                    esc_manager.set_protocol(types.ESC_PROTOCOL_BOOTLOADER)
                    esc_manager.set_baudrate(baud)
                except Exception as e:
                    print(e)
                    continue

                # request bootloader version and see if there is a response
                time.sleep(0.025)
                if esc_manager.detect_bootloader():
                    esc_manager.close()
                    self.protocol_type = 'bootloader'
                    return (port, baud)

                esc_manager.close()

        return (None, None) #no ESCs detected


if __name__ == "__main__":
    scanner = EscScanner()
    scanner.scan()

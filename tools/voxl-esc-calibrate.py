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
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='ESC Calibration Script')
parser.add_argument('--device',              required=False, default=None)
parser.add_argument('--baud_rate',           required=False, default=None)
parser.add_argument('--id',        type=int, required=False, default=0)
parser.add_argument('--pwm-min',   type=int, required=False, default=10)
parser.add_argument('--pwm-max',   type=int, required=False, default=90)
args = parser.parse_args()

devpath  = args.device
baudrate = args.baud_rate
esc_id   = args.id
PWM_MIN  = args.pwm_min
PWM_MAX  = args.pwm_max

if devpath is None:
    scanner = SerialScanner()
    (devpath, baudrate) = scanner.scan()

    if devpath is not None and baudrate is not None:
        print ''
        print 'ESC(s) detected on port: ' + devpath + ' using baudrate: ' + str(baudrate)
        print 'Attempting to open...'
    else:
        print 'No ESC(s) detected, exiting.'
        sys.exit(0)

#check input arguments
if PWM_MIN < 10 or PWM_MIN > 50:
    print 'start power must be between 10 and 50'
    sys.exit(0)

if PWM_MAX < 10 or PWM_MAX > 100:
    print 'end power must be between 10 and 100'
    sys.exit(0)

if PWM_MAX < PWM_MIN:
    print 'end power must be greater than start power'
    sys.exit(0)

# PWM goal
PWM_STEP       = 1
STEPDURATION   = 0.50 #seconds
TRANSITIONTIME = 0.40

# create ESC manager and search for ESCs
manager = EscManager()
manager.open(devpath, baudrate)

# wait a little to let manager find all ESCs
time.sleep(1)
num_escs = len(manager.get_escs())
if num_escs < 1:
    print 'No ESCs detected--exiting.'
    sys.exit(0)

esc = manager.get_esc_by_id(esc_id)
if esc is None:
    print 'Specified ESC ID not found--exiting.'
    sys.exit(0)

# warn user
print 'WARNING: '
print 'This test requires motors to spin at high speeds with'
print 'propellers attached. Please ensure that appropriate'
print 'protective equipment is being worn at all times and'
print 'that the motor and propeller are adequately isolated'
print 'from all persons.'
print ''
print 'For best results, please perform this test at the'
print 'nominal voltage for the battery used.'
print ''
response = raw_input('Type "Yes" to continue: ')
if response not in ['yes', 'Yes', 'YES']:
    print 'Test canceled by user'
    sys.exit(0)

# get ESC software version. sw_version < 20 means gen1 ESC, otherwise gen2
sw_version = esc.get_versions()[0]

# spin up
manager.set_highspeed_fb(esc_id)  #tell ESC manager to only request feedback from this ID (so we get feedback 4x more often)
esc.set_target_power(10)
t_start = time.time()
while time.time() - t_start < 1.0:
    time.sleep(0.05)
    manager.send_pwm_targets()

measurements = []
t_test_start= time.time()

# ramp up from min to max
pwm_now = 10
while pwm_now < PWM_MAX:
    esc.set_target_power(pwm_now)
    t_start = time.time()
    print ''
    while time.time() - t_start < STEPDURATION:
        time.sleep(0.01)
        manager.send_pwm_targets()
        if pwm_now >= PWM_MIN and time.time() - t_start >= TRANSITIONTIME:
            measurements.append(
                [esc.get_power(), esc.get_rpm(), esc.get_voltage(), esc.get_current()])
            print 'POW: %d, RPM: %.2f, Voltage: %.2fV, Current: %.2fA' % (esc.get_power(), esc.get_rpm(), esc.get_voltage(), esc.get_current())
    pwm_now += PWM_STEP

# close the manager and UART thread
manager.close()
t_test_stop= time.time()
print 'Test took %.2f seconds' % (t_test_stop-t_test_start)

# parse measurements
pwms     = [data[0] for data in measurements]
rpms     = [data[1] for data in measurements]
voltages = [data[2] for data in measurements]
currents = [data[3] for data in measurements]

#reported power is 0-100, but in ESC firmware it is 0-1000
motor_voltages = [pwms[i]*10.0/999.0*(voltages[i]*1000) for i in range(len(pwms))]
#print motor_voltages

# linear fit or quadratic fit
ply = np.polyfit(rpms, motor_voltages, 2)
motor_voltages_fit = np.polyval(ply, rpms)

# print corresponding params
print 'Quadratic fit: motor_voltage = a2*rpm_desired^2 + a1*rpm_desired + a0'
print '    a0 = ' + str(ply[2])
print '    a1 = ' + str(ply[1])
print '    a2 = ' + str(ply[0])
print 'ESC Params (after scaling):'
print '    pwm_vs_rpm_curve_a0 = ' + str(ply[2])
print '    pwm_vs_rpm_curve_a1 = ' + str(ply[1])
print '    pwm_vs_rpm_curve_a2 = ' + str(ply[0])

# plot results if possible
try:
  import matplotlib.pyplot as plt
except:
  print('In order to plot the results, install the Python "matplotlib" module')
  sys.exit(0)

# plot the results
plt.plot(rpms, motor_voltages, 'bo')
plt.plot(rpms, motor_voltages_fit)
plt.xlabel('Measured RPM')
plt.ylabel('Commanded Motor Voltage (mV)')
plt.title('Motor Voltage vs. RPM Test')
plt.legend(['Data', 'Fit'], loc=2)
plt.ylim([0, np.max(motor_voltages)+1000])
#plt.show()

plt.figure()
plt.plot(pwms, rpms, 'bo')
plt.xlabel('Commanded PWM (x/100)')
plt.ylabel('Measured RPM')
plt.title('RPM vs. PWM Test')
plt.show()

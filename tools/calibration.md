# Hardware Setup
- use a power supply (not battery.. for safety)
- set voltage to nominal battery voltage (7.5V for 2S, 11.3V for 3S, 15V for 4S)
- make sure the power supply can handle the maximum motor current. If not, you will see the voltage drop towards the end of the test (power supply limiting) and the calibration will be invalid
- use appropriate wire gauge for the maximum current (usually 18 or 16 gauge is OK)
- connect power connector from power supply to ESC
- connect UART adapter to PC / Laptop
- apply power and make sure there are no unusual sounds or smell
- check current when motors not spinning

# Software Setup
- download voxl-esc tools and install any required prerequisites
 - see instructions at https://gitlab.com/voxl-public/voxl-esc/-/tree/master/tools
- locate an existing tuning params file that most closely matches the motor that you have
- make a copy of the existing params file and update it if needed
    - specifically, make sure that ```num_cycles_per_rev``` is correct (usually 6 or 7 corresponding to number of pole pairs), otherwise RPM will not be calculated correctly
    - set ```vbat_nomival_mv``` to nominal battery voltage
    - leave other parameters the same, as they may not be known
    - upload the params file ```python voxl-esc-upload-params.py --params-file ../params/<params_file>.xml```

# Detect ESC and Perform a Quick Spin Test
- detect the ESCs, make sure the software is the same version
 - ```python voxl-esc-scan.py```
- do a quick spin at lower power (10%)
 - ```python voxl-esc-spin.py --id 0 --power 10```
 - make sure the propeller is spinning in the correct direction (CW or CCW depending on propeller). Reverse one pair of motor wires to switch direction if needed
 - compare RPM to what is reported by tachometer
 - do not command very large power (open loop commands), since it will result in a very large step (less than 30)

## Calibrate ESC
- wear safety glasses
  - make sure the propeller is clear of any obstacles and there are no items that can become airborne due to high air flow
- calibrate the ESC's feed-forward curve
 - ```python voxl-esc-calibrate.py --id 0 --pwm-min 10 —-pwm-max 95```
  - this will step the motor through a range of power from 10% to 95%


## Update and Upload Calibration File
- update calibration parameters file printed by the calibration script
 - ```pwm_vs_rpm_curve_a0, pwm_vs_rpm_curve_a1, pwm_vs_rpm_curve_a2```
 - ```min_rpm``` and ```max_rpm```. Note that max rpm will depend on battery voltage, but it is a good practice to just use maximum RPM at nominal voltage (or lowest voltage). minimum rpm can be taked from 10% power and maximum from 95% power. However, do not command 95% power using voxl-esc-spin.py, since there is no limiting in power mode (as opposed to RPM) and motor can burn out.
- upload the calibration file to all ESCs. This will also reboot all the ESCs.
 - ```python voxl-esc-upload-params.py --params-file ../params/<params_file>.xml```
- validate the esc parameters: ```python voxl-esc-verify-params.py```

## Test ESC using RPM commands
- choose RPM to test according to motor limits
- with proper tuning, the motor should track RPM very closely (typically within 100 RPM across the whole range)
- voltage compensation is automatic, so try adjusting voltage up and down 1-2 volts and RPM tracking should remain constant
```
python voxl-esc-spin.py --id 0 --rpm 5000
...
[0] RPM: 4999, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.79C, CURRENT: 0.18A
[0] RPM: 4999, PWR: 20, VBAT: 11.45V, TEMPERATURE: 31.80C, CURRENT: 0.22A
[0] RPM: 5001, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.82C, CURRENT: 0.14A
[0] RPM: 5001, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.82C, CURRENT: 0.14A
[0] RPM: 4979, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.76C, CURRENT: 0.21A
[0] RPM: 5005, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.67C, CURRENT: 0.22A
[0] RPM: 5011, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.64C, CURRENT: 0.16A
[0] RPM: 5011, PWR: 20, VBAT: 11.44V, TEMPERATURE: 31.64C, CURRENT: 0.16A
...
```

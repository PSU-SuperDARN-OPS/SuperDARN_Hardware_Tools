# Cable Length Calibration

## Introduction
The cable length calibration program is to match the lengths of coaxial cable 
for an antenna array. 

## Description
The program connects to a Keysight E5062A ENA Vector Network Analyzer over a 
LAN telnet connection. The VNA will measure the length of the cable attached
and then return the length that needs to be cut off to achieve the desired 
length.

## Interface
The program is controlled through command line arguments. The are as follows:

* `--cal` 
If this is set, then the VNA will run through a calibration before taking measurements.
* `--meas`
If this is set, then the program will only measure the cable lengths
* `--vna_ip`
Specify a different IP address. The default is 192.168.11.3 (set in vna_control.py)
* `--data_dir`
Specify the directory data is saved. The default is 'sandbox'.
* `--avg`
Enables averaging measurements. Specify the number of measurements to average.
* `--cables`
Specify the number of cables to be measured. The default is 1. If this is more than 1,
then the program will prompt you to connect each cable.
* `--vel`
Specify the velocity factor of the cable. The default is 0.87.
* `--target_len`
Specify the target length in meters. 
* `--tol`
Specify the tolerance of the cable length in meters.
# stupid function to control qnx box over ssh commands to set beam numbers
# copy over ssh keys to make this faster

import os
import time

QNX_IP = '192.168.0.210'
BEAM_SETTLE = .5

# radar 1 is east, radar 2 is west

def qnx_setbeam(ip, beam, radar = 2):
    os.system('ssh root@' + ip + ' "/root/current_ros/dio_beam_direction -b ' + str(int(beam)) + ' -r ' + str(int(radar)) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)


def qnx_setmemloc(ip, loc, rack=1):
    os.system('ssh radar@' + ip + ' "/home/radar/bin/dio_beam_direction -b ' + str(int(loc)) + ' -r ' + str(rack) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)

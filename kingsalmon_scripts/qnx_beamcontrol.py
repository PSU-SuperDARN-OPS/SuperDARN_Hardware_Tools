# stupid function to control qnx box over ssh commands to set beam numbers
# copy over ssh keys to make this faster

import os
import time

QNX_IP = 'azores-qnx'
BEAM_SETTLE = .5

def qnx_setbeam(ip, beam):
    os.system('ssh root@' + ip + ' "/root/current_ros/dio_beam_direction -b ' + str(int(beam)) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)


def qnx_setmemloc(ip, loc, rack=1):
    os.system('ssh radar@' + ip + ' "/home/radar/bin/dio_beam_direction -b ' + str(int(loc)) + ' -r ' + str(rack) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)

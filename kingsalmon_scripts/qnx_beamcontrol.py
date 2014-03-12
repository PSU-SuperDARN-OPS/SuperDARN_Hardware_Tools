# stupid function to control qnx box over ssh commands to set beam numbers
# copy over ssh keys to make this faster

import os
import time

QNX_IP = '192.168.0.4'
BEAM_SETTLE = .1

def qnx_setbeam(ip = QNX_IP, beam):
    os.system('ssh root@' + ip + ' "/root/current_ros/dio_beam_direction -b ' + str(int(beam)) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)


def qnx_setmemloc(ip = QNX_IP, loc):
    os.system('ssh radar@' + ip + ' "/home/radar/bin/dio_beam_direction -b MemLoc -r ' + str(int(loc)) + ' >/dev/null 2>/dev/null"')
    time.sleep(BEAM_SETTLE)

# quick script to measure cable lengths with the VNA to help with cutting
# jtklein@alaska.edu, jon klein, 10/2013

from __future__ import division
from vna_control import *
from numpy import mean, deg2rad, pi, floor
import argparse, logging, os, sys, csv, datetime, pdb

FSTART = 5e6 
FSTOP = 25e6

SWEEP_CENTER = 15e6
SWEEP_SPAN = 20e6
SWEEP_POINTS = 1201
TIMEOUT = max(0.1,0.04/201.0 * SWEEP_POINTS)
VELOCITY_FACTOR = .87
C = 3e8
TOLERANCE = .02 # meters of cable length tolerance
CABLE_LEN = 150 # cable length in meters
APERTURE = 2.0 # smoothing aperture for vna time delay measurements

FEET_PER_METER = 3.28084
INCHES_PER_METER = FEET_PER_METER * 12

def printlog(s):
    print s
    logging.info(s)


# measures the length of a cable given a vna and a velocity factor
# returns estimated length in meters
def get_cablelen(vna, vel, freqs):
    vna_clearave(vna)
    vna_trigger(vna, TIMEOUT, args.avg)

    clen_delay = calc_cablelen_delay(vna, vel)
    clen_ephase = calc_cablelen_ephase(vna, vel, freqs)

    print 'delay: ' + str(clen_delay)
    print 'ephase: ' + str(clen_ephase)

    return clen_delay

def calc_cablelen_ephase(vna, vel, freqs, fstart = FSTART, fstop = FSTOP):
    ephase = vna_readextendedphase(vna)
    fstep = freqs[1] - freqs[0]
    fstartidx = int((fstart - freqs[0])/fstep)
    fstopidx = int((fstop - freqs[0])/fstep)

    dphase = -deg2rad(ephase[fstopidx] - ephase[fstartidx])
    dfreq = 2 * pi * (fstop - fstart)
    
    tdelay = dphase / dfreq
    clen_ephase = tdelay * C * vel / 2.0
    return clen_ephase

def calc_cablelen_delay(vna, vel):
    tdelay = vna_readtimedelay(vna)
    inset = int(len(tdelay) * 1.1 * APERTURE / 100)
    tavg = mean(tdelay[inset:-inset])
    clen_delay = tavg * C * vel / 2.0
    return clen_delay

if __name__ == '__main__':
    # setup arguement parser and parse arguements
    parser = argparse.ArgumentParser()

    parser.add_argument("--cal", action="count", help="run through calibration on vna before taking measurements", default=0)
    parser.add_argument("--meas", action="count", help="only measure length of cable, then exit", default=0)
    parser.add_argument("--vnaip", help="specify vna ip address", default=VNAHOST)
    parser.add_argument("--ddir", help="specify a directory to save the data in", default='sandbox')
    parser.add_argument("--avg", type=int, help="specify count to average", default=1)
    parser.add_argument("--cables", type=int, help="specify number of cables to measure", default=1)
    parser.add_argument("--vel", type=float, help="specify a velocity factor for the cable", default=VELOCITY_FACTOR)
    parser.add_argument("--tlen", type=float, help="specify a target cable length (in meters)", default=CABLE_LEN)
    parser.add_argument("--tol", type=float, help="specify cable length tolerance (in meters)", default=TOLERANCE)
    args = parser.parse_args()

    # sanity check arguements 
    if args.avg < 1:
        sys.exit("error: average count is less than 1")

    if not os.path.exists(args.ddir):
        sys.exit("error: data directory does not exist: %s" % (args.ddir))

    if args.cables < 1:
        sys.exit("error: cable count is less than 1")
    
    if args.vel > 1 or args.vel < 0:
        sys.exit("error: cable velocity factor violates known physics")


    if args.tlen == 0:
        sys.exit("error: target cable length is zero meters")

    # setup logging and csv file writing
    logging.basicConfig(format='%(asctime)s %(message)s', filename= args.ddir + '/cable_len' + str(datetime.date.today()) + '.log', filemode='a')

    csvfile = open('cable_lens' + str(datetime.date.today()) + '.csv', 'a')
    csvwriter = csv.writer(csvfile, delimiter = ',')
    
    csvwriter.writerow(["cable length log", str(datetime.date.today())])
    csvwriter.writerow(["cable #", "cable length (m)"])

    # open connection with vna
    vna = lan_init(args.vnaip)

    # preset vna if calibrating
    if args.cal:
        vna_preset(vna)

    # init vna measurements
    vna_init(vna, 'S22')

    # configure vna measurements (add smoothing to time delay channel, enable averaging) 
    vna_setspan(vna, SWEEP_SPAN, SWEEP_CENTER, SWEEP_POINTS)
    vna_setave(vna, args.avg)
    vna_enableave(vna, True)
    vna_smoothapeture(vna, 2, APERTURE)
    vna_enablesmoothing(vna, 2, True)
   
    freqs = vna_readspan(vna)

    # calibrate VNA if run with --cal
    if args.cal:
        printlog('calibrating VNA')
        vna_through_cal(vna)
        vna_trigger(vna, TIMEOUT, args.avg)
    
    cable_lens = {}

        
    for p in range(args.cables):
        p = int(raw_input('connect and enter a cable number and then press enter to continue... '))

        clen = get_cablelen(vna, args.vel, freqs)
        printlog('initial cable %d length is %.4f of %.4f meters' % (p, clen, args.tlen))
        
        if(args.meas):
            break

        while(True):
            if abs(clen - args.tlen) < args.tol or args.tlen > clen:
                if args.tlen > clen:
                    printlog('cable shorter than target length, breaking')
                printlog('cable %d final length is %.4f of %.4f meters' % (p, clen, args.tlen))
                cable_lens[p] = clen
                csvwriter.writerow([p, clen])
                break

            clen = get_cablelen(vna, args.vel, freqs)
            error = clen - args.tlen
            printlog('cable %d is %.4f of %.4f meters' % (p, clen, args.tlen))
            feeterror = FEET_PER_METER * (error / 2.0)
            incherror = (feeterror - int(feeterror)) * 12

            printlog('cable %d error is %.4f, cut %.4f meters (%.4f feet and %.4f inches)' % (p, error, error / 2.0, floor(feeterror), incherror))
            raw_input('press enter to continue\n')


    lan_close(vna)


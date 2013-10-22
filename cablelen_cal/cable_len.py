# quick script to measure cable lengths with the VNA to help with cutting
# untested
# jtklein@alaska.edu, jon klein, 10/2013

from vna_control import *
import argparse, logging, os, sys 

SWEEP_CENTER = 15e6
SWEEP_SPAN = 20e6
SWEEP_POINTS = 1201
TIMEOUT = max(0.1,0.04/201.0 * SWEEP_POINTS)
VELOCITY_FACTOR = .87
C = 3e8
TOLERANCE = .02 # meters of cable length tolerance
CABLE_LEN = 150 # cable length in meters
APERTURE = 2.0 # smoothing aperture for VNA time delay measurements

FEET_PER_METER = 3.28084
INCHES_PER_METER = FEET_PER_METER * 12


# measures the length of a cable given a VNA and a velocity factor
# returns estimated length in meters
def get_cablelen(vna, vel):
    vna_clearave(vna)
    vna_trigger(vna, TIMEOUT, args.avg)

    tdelay = vna_readtimedelay(vna)

    inset = int(len(t_delay) * 1.1 * APERTURE / 100)
    tavg = avg(tdelay[inset:-inset])
    clen = tavg / (2 * C * vel)

    return clen


if __name__ == '__main__':
    # setup arguement parser and parse arguements
    parser = argparse.ArgumentParser()

    parser.add_argument("--cal", action="count", help="run through calibration on VNA before taking measurements", default=0)
    parser.add_argument("--vnaip", help="specify VNA ip address", default=VNAHOST)
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

    logging.basicConfig(format='%(asctime)s %(message)s')
    logging.basicConfig(filename= args.ddir + '/cable_len.log', filemode='w', level=logging.DEBUG)

    # open connection with VNA
    vna = lan_init(args.vnaip)

    # preset VNA if calibrating
    if args.cal:
        vna_preset(vna)

    # init VNA measurements
    vna_init(vna)

    # configure VNA measurements (add smoothing to time delay channel, enable averaging) 
    vna_setspan(vna, SWEEP_SPAN, SWEEP_CENTER, SWEEP_POINTS)
    vna_setave(vna,args.avg)
    vna_enableave(vna,True)
    vna_smoothapeture(vna,2,APERTURE)
    vna_enablesmoothing(vna,2,True)
    
    # calibrate VNA if run with --cal
    if args.cal:
        logging.info('calibrating VNA')
        vna_through_cal(vna)
        vna_trigger(vna, TIMEOUT, args.avg)
    
    for p in range(args.cables):
        p = int(raw_input('connect and enter a cable number and then press enter to continue... '))

        clen = cable_length(vna)
        logging.info('initial cable %d length is %.2f of %.2f meters' % (p, clen, tlen))

        while abs(clen - ars.tlen) > args.tol:
            clen = cable_length(vna)
            error = tlen - clen
            logging.info('cable %d is %.2f of %.2f meters' % (p, clen, tlen))
            logging.info('cable %d error is %.2f, cut %.2f meters' % (p, error, error / 2.0))
            raw_input('press enter to continue\n')

    lan_close(vna)


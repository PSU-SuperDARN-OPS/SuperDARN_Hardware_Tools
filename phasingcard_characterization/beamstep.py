# jon klein, jtklein@alaska.edu
# measures the phase offset from channel 2 to channel 1, and the amplitude (vpp) at each beam
# configure site settings to place rising edge midway through pulse to measure

# channel 1 : power divided input signal to phasing card (with 50 ohm termination)
# channel 2 : output of phasing card (with 50 ohm termination)
# channel 4 : scope sync   

import os
import time
import pickle
import logging
import pdb
from scope_control import *

VERSION = 0
DATA_FOLDER = 'data/'
MAX_BEAMS = 1
CARDS = [16]
FREQS = [10000,11000,12000,13000,14000,15000] # kHz
RACK = 'azw'

# delays are in seconds
ROS_STARTUP_DELAY = 5
VPP_SAMPLE_DELAY = .5
INTEGRATION_TIME = 1

# thresholds to compare measurements against and log any violations
BEAMVPP_THRESHOLD = 1.4
INPUTVPP_THRESHOLD = 1.4
DISTORTION_THRESHOLD = .02

# scope settings, units in volts
SCOPE_SCALE = .5
SCOPE_OFFSET = 0

# scope channels
INPUT_CHANNEL = 1
OUTPUT_CHANNEL = 2

# phase averaging

# measure the gain and phase through a phasing card across frequency and beams
def measure_phasingcard(int_time = INTEGRATION_TIME, card = -1):
    phase = []
    vout_vpp = []
    vin_vpp = []
    distortion = []
    thd = []
    for f in FREQS:
        vouts = []
        vins = []
        phases = []
        distorts = []
        thds = []

        for b in range(MAX_BEAMS):
            # digitize samples
            scope_clear(ser)
            scope_digitize(ser, [1,2])
            os.system('diagnosticscan -stid ' + RACK + ' -single -fixfrq ' + str(f) + ' -sb ' + str(b) + ' -eb ' + str(b) + ' -intsc ' + str(int(int_time)) + ' -nowait >/dev/null 2>/dev/null &')
            time.sleep(2)
            data = scope_getraw(ser, [1,2])
            
            # analyze digitized samples
            vouts.append(scope_analyzevpp(data,OUTPUT_CHANNEL))
            vins.append(scope_analyzevpp(data,INPUT_CHANNEL))
            phases.append(scope_analyzephase(data,OUTPUT_CHANNEL,INPUT_CHANNEL))
            distorts.append(scope_analyzedistortion(data, OUTPUT_CHANNEL))
            thds.append(scope_analyzethd(data, OUTPUT_CHANNEL))

            print('card ' + str(card) + ', frequency ' + str(f) + ', beam ' + str(b) + ', vpp: ' + str(vouts[-1])[:5] + ', phase: ' + str(phases[-1])[:5] +  ', vin: ' + str(vins[-1])[:5] + ' distortion: ' + str(distorts[-1])[:5] + ' thd: ' + str(thds[-1])[:5])

            # sanity check measurements and log odd behavior
            if vouts[-1] < BEAMVPP_THRESHOLD:
                logging.warning('measured beam %s, card %s, freq %s, ouput amplitude of %s', str(b), str(card), str(f), str(vouts[-1]))

            if vins[-1] < INPUTVPP_THRESHOLD:
                logging.warning('measured input vpp on card %s, beam %s, freq %s, ouput amplitude of %s', str(card), str(b), str(f), str(vins[-1]))
            
            if abs(distorts[-1]-1) > DISTORTION_THRESHOLD:
                logging.warning('vpp_predicted_from_rms/vpp_measured ratio exceeds threshold on card %s beam %s freq %s, ratio of %s', str(card), str(b), str(f), str(distorts[-1]))
            
        phase.append(phases)
        vout_vpp.append(vouts)
        vin_vpp.append(vins)
        distortion.append(distorts)
        thd.append(thds)

    return {'vout_vpp':vout_vpp,'phase':phase,'vin_vpp':vin_vpp,'distortion':distortion, 'thd':thd}

if __name__ == "__main__":
    ser = scope_init()
    scope_preset(ser)
    filename = raw_input('enter a filename to save the data to: ')    

    # set timebase
    scope_settimebase(ser, 1) # set timebase in microseconds (.5 is 5 cycles at 10 MHz)

    # configure channels 1 and 2 for 500 mV/div
    scope_setchannel(ser, INPUT_CHANNEL, SCOPE_SCALE, SCOPE_OFFSET)    
    scope_setchannel(ser, OUTPUT_CHANNEL, SCOPE_SCALE, SCOPE_OFFSET)    
    
    # setup timebase, trigger channel, and triggering settings
    scope_setchannel(ser, 4, 1, 5)
    scope_edgetrigger(ser, 4)
    
    # save some information about the measurements
    pickle_dict = {}
    pickle_dict['INTEGRATION_TIME'] = INTEGRATION_TIME
    pickle_dict['CARDS'] = CARDS
    pickle_dict['MAX_BEAMS'] = MAX_BEAMS 
    pickle_dict['RACK'] = RACK
    pickle_dict['FREQS'] = FREQS
    pickle_dict['VERSION'] = VERSION
    pickle_dict['CARD_DATA_FORMAT'] = ['index cardN_opt/unopt data arrays by frequency, see FREQS list for a list of frequencies']
    
    # setup logging 
    logging.basicConfig(format='%(asctime)s %(message)s', filename=(DATA_FOLDER + filename + '.log'), level=logging.INFO)
    logging.info('started logging beamstep, %s freqs, max beams %s, %s cards, %s', str(FREQS), str(MAX_BEAMS), str(CARDS), RACK)
    logging.info('saving to file prefix %s%s', DATA_FOLDER, filename)
    
    # iterate through cards and make some measurements
    for c in CARDS:
        raw_input('please connect main array card ' + str(c) + ' then press enter to continue')
        
        os.system('ssh root@azores-qnx.gi.alaska.edu "cp ~/operational_radar_code/azores/site_data/site.ini.cal ~/operational_radar_code/azores/site_data/site.ini; ~/operational_radar_code/azores/stop.ros; nohup ~/operational_radar_code/azores/start.ros &"')
        time.sleep(ROS_STARTUP_DELAY)
        print('qnx started, measuring phasing cards..')

        pickle_dict['card' + str(c) + 'opt'] = measure_phasingcard(card=c)

        os.system('ssh root@azores-qnx.gi.alaska.edu "cp ~/operational_radar_code/azores/site_data/site.ini.uncal ~/operational_radar_code/azores/site_data/site.ini; ~/operational_radar_code/azores/stop.ros; nohup ~/operational_radar_code/azores/start.ros &"')
        time.sleep(ROS_STARTUP_DELAY)
        pickle_dict['card' + str(c) + 'unopt'] = measure_phasingcard(card=c)
    
    logging.info('measurements complete, stopping logging') 
    # save data in a pickle
    pickle.dump(pickle_dict, open(DATA_FOLDER + filename + '.' + RACK + '.pickle', 'wb')) 
    

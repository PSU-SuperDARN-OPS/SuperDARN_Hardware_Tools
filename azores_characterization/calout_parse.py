# reads output from optimized card calibration, builds lookup table for memory locations
# create dictionary[frequency] = memloc for beam zero


WINDOWCAL_MEMBASE = 64
WINDOWCAL_MEMSTEP = 32
WINDOWCAL_FREQSTEP= .25e6 # hz
WINDOWCAL_FREQBASE = 8.0e6 # hz

def get_memaddr(freq, beam):
    return int((freq - WINDOWCAL_FREQBASE) / (WINDOWCAL_FREQSTEP)) * WINDOWCAL_MEMSTEP + WINDOWCAL_MEMBASE + beam

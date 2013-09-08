import csv
import os
import datetime

class csv_data:
    card=None
    beam=None
    sweep_count=None
    ave_count=None
    ave_enable=None
    smoothing_percent=None
    smoothing_enable=None
    tdelay=None
    phase=None
    ephase=None
    mlog=None
    timestamp=None
    freqs=None
    freq_start=None
    freq_end=None

def write_csv(directory,data):
    if data.timestamp is None: data.timestamp=datetime.datetime.now()
    if data.freqs is None: data.freqs=[]
    if data.tdelay is None: data.tdelay=[]
    if data.phase is None: data.phase=[]
    if data.ephase is None: data.ephase=[]
    if data.mlog is None: data.mlog=[]
    print directory,data.card,data.beam
    if not os.path.exists(directory):
        print "directory does not exist: %s" % (directory)
        return
    if not os.path.isdir(directory):
        print "Not a directory: %s" % (directory)
        return
    card_dir=os.path.join(directory,"card_%02d" % (data.card)) 
    if not os.path.exists(card_dir):
        os.mkdir(card_dir)  
    if not os.path.isdir(card_dir):
        print "Not a directory: %s" % (card_dir)
        return
    beam_file=os.path.join(card_dir,"beam_%02d.csv" % (data.beam)) 
    csv_file=open(beam_file,"w")
    csv_writer=csv.writer(csv_file,delimiter="\t")
    header=[
        "Card:",data.card,
        "Beam:",data.beam,
        "Timestamp:","%s" % (data.timestamp),
    ]
    csv_writer.writerow(header)
    header=[
        "Sweep Count:",data.sweep_count,"Start [Hz]:",data.freq_start,"End: [Hz]",data.freq_end,
    ]
    csv_writer.writerow(header)
    header=[
        "Ave Enable:",data.ave_enable,
        "Ave Count:",data.ave_count,
    ]
    csv_writer.writerow(header)
    header=[
        "Time Delay Smoothing Enable:",data.smoothing_enable,
        "Time Delay Smoothing Percent:",data.smoothing_percent,
    ]
    csv_writer.writerow(header)
    labels=[
        "Freq [Hz]",
        "Time Delay [sec]",
        "Phase [deg]",
        "Extended Phase [deg]",
        "Mag Log [dB]",
    ]
    csv_writer.writerow(labels)
    for i in xrange(len(data.freqs)):
        row=[
            data.freqs[i],
            data.tdelay[i],
            data.phase[i],
            data.ephase[i],
            data.mlog[i],
        ]
        csv_writer.writerow(row)
    csv_file.close()
    
    return

if __name__ == '__main__':
    directory="/tmp/ksr_test"
    data=csv_data()
    data.card=0
    data.beam=12
    data.sweep_count=1201
    data.freq_start=5E6
    data.freq_end=25E6
    data.ave_enable=True
    data.ave_count=16
    data.smoothing_enable=True
    data.smoothing_percent=5.0
    data.freqs=[0,1,2,3,4,5]
    data.tdelay=[0,-1,-2,-3,-4,-5]
    data.phase=[0,0,0,0,0,0]
    data.ephase=[0.,10.,20.,30.,40.,50.]
    data.mlog=[0,100,200,300,400,500]

    write_csv(directory,data)

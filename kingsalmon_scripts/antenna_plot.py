from csv_utils import *
import pylab as p
import sys
import pdb
directory="./adw_ants"
plotdir="adakplots"
radar="ADW"
maxbeams = 1
cards = range(20)#[6]
plot_directory=os.path.join(directory,plotdir)
if not os.path.exists(plot_directory): os.mkdir(plot_directory)

colors={0:"red",1:"blue",2:"black",3:"green",4:"cyan",5:"yellow"}

for bmnum in range(len(cards)):
    p.figure(400+bmnum)
    p.clf()

    p.figure(300+bmnum)
    p.clf()

    p.figure(500)
    p.clf()

for bmnum in range(maxbeams):
  p.figure(104)
  p.clf()
  for card in cards: 
    data_main=csv_data()
    data_main.card=card
    data_main.beam=bmnum
    read_csv(directory,data_main)
    freqs=p.array(data_main.freqs)

    df=freqs[1]-freqs[0]
    
    main_tdelay=p.array(data_main.tdelay)
    main_ephase=p.array(data_main.ephase)
    main_log=p.array(data_main.mlog)

    p.figure(500)

    p.plot(freqs*1E-6,main_log,color=colors[ card % 6 ],label="antenna %02d" % (card) )

    p.figure(400+card)
    p.plot(freqs*1E-6,main_log,color=colors[ card % 6 ],label="antenna %02d" % (card) )

    p.figure(300+card)
    p.plot(freqs*1E-6,1E6 * main_tdelay,color=colors[ card % 6 ],label="antenna %02d" % (card) )


  p.figure(500)
  p.grid(True)
  p.legend(loc=4)
  ax=p.gca()
  ax.set_xlim((8,20))
  ax.set_ylim((-25,0))
  p.xlabel("Freq [MHz]")
  p.ylabel("S22 [db]")
  p.title("%sS22 of antenna, from radar shack\n Beam %d" % \
      (radar,data_main.beam))
  figfile=os.path.join(plot_directory,"antenna_s22.png")
  p.savefig(figfile)
  for ant in cards:
      p.figure(400 + ant)
      p.grid(True)
      p.legend(loc=4)
      ax=p.gca()
      ax.set_xlim((8,20))
      ax.set_ylim((-25,0))
      p.xlabel("Freq [MHz]")
      p.ylabel("S22 [db]")
      p.title("%s S22 of antenna %d, from radar shack" % \
          (radar,ant))
      figfile=os.path.join(plot_directory,"antenna%d_s22.png" % (ant))
      p.savefig(figfile)

      p.figure(300 + ant)
      p.grid(True)
      p.legend(loc=4)
      ax=p.gca()
      ax.set_xlim((8,20))
      ax.set_ylim((0,3))
      p.xlabel("Freq [MHz]")
      p.ylabel("S22 [db]")
      p.title("%s time delay of antenna %d (us), from radar shack" % \
          (radar,ant))
      figfile=os.path.join(plot_directory,"antenna%d_delay.png" % (ant))
      p.savefig(figfile)


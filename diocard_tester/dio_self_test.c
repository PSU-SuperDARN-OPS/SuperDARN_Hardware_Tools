// test program for dio cards
// attempts to find broken input/ouput pins when groups of ports are jumpered together
// jon klein, jtklein@alaska.edu, 7/2013
// modified from dio_output_test.c by jef spaleta

#include <errno.h>
#include <stdarg.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <stdlib.h>
#include <signal.h>
#include <math.h>
#include <netdb.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <hw/pci.h>
#include <hw/inout.h>
#include <sys/neutrino.h>
#include <sys/mman.h>
#include "registers.h"

#define PORTS 5 // number of ports on DIO card (nominally 5?)


int32 dio_portest(uint32 IOBASE, uint08 portout, uint08 portin, uint08 pattern);
int init_dio(void);

int init_dio(void)
{
    struct		_clockperiod new, old;
    struct		timespec start_p, start;
    int		        temp, pci_handle,  IRQ;
    unsigned int	mmap_io_ptr,IOBASE;

    /* SET THE SYSTEM CLOCK RESOLUTION AND GET THE START TIME OF THIS PROCESS */
    new.nsec=10000;
    new.fract=0;
    temp=ClockPeriod(CLOCK_REALTIME,&new,0,0);
    if(temp==-1){
        perror("Unable to change system clock resolution");
    }

    temp=clock_gettime(CLOCK_REALTIME, &start_p);
    if(temp==-1){
        perror("Unable to read sytem time");
    }
    temp=ClockPeriod(CLOCK_REALTIME,0,&old,0);

    /* OPEN THE PLX9656 AND GET LOCAL BASE ADDRESSES */
    fprintf(stderr,"PLX9052 CONFIGURATION ********************\n");
    clock_gettime(CLOCK_REALTIME, &start);
    temp=_open_PLX9052(&pci_handle, &mmap_io_ptr, &IRQ, 1);
    IOBASE=mmap_io_ptr;
    if(temp==-1){
        fprintf(stderr, "	PLX9052 configuration failed");
    }
    else{
        fprintf(stderr, "	PLX9052 configuration successful!\n");
    }

    return IOBASE;
}

int32 dio_porttest(uint32 IOBASE, uint08 portout, uint08 portin, uint08 pattern)
{
    uint08 a, b, c;
    int32 returnval = 0;

    // setup input port
    out8(IOBASE + CTRL_GRP + GRP_MLT * portin, DIO_INPUT * (PORTA + PORTB + PORTC_LO + PORTC_HI)); 
    
    // set output port as all high
    out8(IOBASE + CTRL_GRP + GRP_MLT * portout, OUTPUT_DISABLE);
    out8(IOBASE + PA_GRP + GRP_MLT * portout, pattern);
    out8(IOBASE + PB_GRP + GRP_MLT * portout, pattern);
    out8(IOBASE + PC_GRP + GRP_MLT * portout, pattern);
    out8(IOBASE + CTRL_GRP + GRP_MLT * portout, OUTPUT_ENABLE);

    // read input ports
    a = in8(IOBASE + PA_GRP + GRP_MLT * portin);
    b = in8(IOBASE + PB_GRP + GRP_MLT * portin);
    c = in8(IOBASE + PC_GRP + GRP_MLT * portin);
   
    // disable output ports
    out8(IOBASE + CTRL_GRP + GRP_MLT * portout, OUTPUT_DISABLE);

    // verify results
    if(a ^ pattern) {
        printf("problem on port a group with input %d and output %d, bit(s) %x\n", portin, portout, a ^ pattern);
        returnval = -1;
    }
    
    if(b ^ pattern) {
        printf("problem on port b group with input %d and output %d, bit(s) %x\n", portin, portout, b ^ pattern);
        returnval = -1;
    }
    
    if(c ^ pattern) {
        printf("problem on port c group with input %d and output %d, bit(s) %x\n", portin, portout, c ^ pattern);
        returnval = -1;
    }
    
    if(!returnval) {
        printf("output on group %d to input on group %d with pattern %x looks fine\n", portout, portin, pattern);
    }

    return returnval;
}


// tests two groups on a dio card
// run as ./dio_selftest group1 group2
// for example, ./dio_selftest 2 3 checks groups 2 and 3
// dio_selftest print out guesses at bad ports and pins

int main(int argc, char **argv)
{
    uint32 IOBASE;
    uint32 i; 
    uint32 rvals = 0;
    uint08 port1, port2;

    // parse arguements, and not in a smart way
    if(argc == 3) {
        port1 = atoi(argv[1]);
        port2 = atoi(argv[2]);
        printf("checking groups %d and %d", port1, port2);
    } else {
        printf("dio_selftest: you must specify two ports which are connected to each other to test\n");
        printf("for example, ./dio_selftest 2 3 will check the inputs and outputs between ports 2 and 3\n");
        return 0;
    }

    // init dio card
    IOBASE = init_dio();
    
    // set all ports as inputs, disable output buffer
    for(i = 0; i < PORTS; i++) {
        out8(IOBASE + CTRL_GRP + GRP_MLT * i, OUTPUT_DISABLE  + PORTA + PORTB + PORTC_LO + PORTC_HI);
    }

    for(i = 0; i < 256; i++) {
     	rvals += dio_porttest(IOBASE, port1, port2, i);
    	rvals += dio_porttest(IOBASE, port2, port1, i);
    } 

    if(rvals) {
	printf("errors found with dio card\n");
    } else {
	printf("hurray! no errors found during test\n");
    }
    return rvals;
}

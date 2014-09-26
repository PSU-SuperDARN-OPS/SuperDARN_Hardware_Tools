#include <stdio.h>

#include <sys/socket.h>
// headers copied from alex's code.. probably don't need all these
#include <uhd/utils/thread_priority.hpp>
#include <uhd/utils/safe_main.hpp>
#include <uhd/utils/static.hpp>
#include <uhd/usrp/multi_usrp.hpp>
#include <uhd/exception.hpp>
#include <boost/thread/thread.hpp>
#include <boost/program_options.hpp>
#include <boost/math/special_functions/round.hpp>
#include <boost/foreach.hpp>
#include <boost/format.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <iostream>
#include <string>
#include <fstream>
#include <complex>
#include <csignal>
#include <cmath>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fftw3.h>

#define verbose 1

// connect rxfe to J24
#define RXFE_MASK 0xFF 
#define RXFE_CONTROL 0x00 // manual control
#define RXFE_AMP_MASK 0xD0
#define RXFE_ATT_MASK 0x3F
#define ATT_D1 4
#define ATT_D2 3
#define ATT_D3 2
#define ATT_D4 1
#define ATT_D5 0
#define AMP_1 7
#define AMP_2 6

// connect to control to J50
#define CONTROL_MASK 0x8D
#define CONTROL_CONTROL 0x00
#define CONTROL_TR_MASK 0x0D
#define CONTROL_FAULT_MASK 0x80

#define TRA (1 << 4)// 7, output
#define TRB (1 << 3)// 9, output 

#define CONTROL_TX (TRA) 
#define CONTROL_RX (TRB)

#define FAULT 7 // 1, input
//
int main(int argc, char *argv[])
{
    uint32_t i,j, fault;
    std::string args;
    args="addr=192.168.10.2";
    
    // create USRP device
    uhd::usrp::multi_usrp::sptr usrp = uhd::usrp::multi_usrp::make(args);
    
    // init USRP
    usrp->set_clock_source("internal");
    usrp->set_time_now(uhd::time_spec_t(0.0));
    if (verbose) std::cout << boost::format("Using Device: %s") % usrp->get_pp_string() << std::endl;
    
    // setup RXFE gpio
    usrp->set_gpio_attr("RXA", "CTRL", RXFE_CONTROL, RXFE_MASK); // set GPIO to manual control
    usrp->set_gpio_attr("RXA", "DDR", RXFE_MASK, RXFE_MASK); // set everybody as outputs
    
    // setup control gpio
    usrp->set_gpio_attr("TXA", "CTRL", CONTROL_CONTROL, CONTROL_MASK); // set GPIO to manual control
    usrp->set_gpio_attr("TXA", "DDR", CONTROL_TR_MASK, CONTROL_TR_MASK); // set TR as outputs 
    usrp->set_gpio_attr("TXA", "DDR", 0x00, CONTROL_FAULT_MASK); // set fault as input 

    // start up with rxfe disabled, rx mode
    usrp->set_gpio_attr("RXA", "OUT", 0x00, RXFE_AMP_MASK);
    usrp->set_gpio_attr("RXA", "OUT", 0xFF, RXFE_ATT_MASK);
    usrp->set_gpio_attr("TXA", "OUT", CONTROL_RX, CONTROL_TR_MASK);
    
    printf("starting cycling!\n");

    // cycle through dio settings
    while(1) {
        for(j = 0; j < 4; j++) {
            usrp->set_gpio_attr("RXA", "OUT", j << 6, RXFE_AMP_MASK);
            for(i = 0; i < 32; i++) {
                
                fault = (usrp->get_gpio_attr("TXA", "READBACK") & CONTROL_FAULT_MASK);
                usrp->set_gpio_attr("RXA", "OUT", i, RXFE_ATT_MASK);

                if(i % 2) {
                    usrp->set_gpio_attr("TXA", "OUT", CONTROL_RX, CONTROL_TR_MASK);
                }
                else {
                    usrp->set_gpio_attr("TXA", "OUT", CONTROL_TX, CONTROL_TR_MASK);
                }

                printf("fault state: %d, att state: %d, tx state %d\n", fault, i, i % 2);
                sleep(1); 
            }
        }
    }

    return 0;
}

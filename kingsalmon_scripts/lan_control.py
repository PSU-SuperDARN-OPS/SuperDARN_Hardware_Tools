import telnetlib, time
VNATIMEOUT = 5 # seconds
VNAHOST = '192.168.17.100'

def lan_init(host):
    tn = telnetlib.Telnet(host)
    time.sleep(.5)
    print "initial response from VNA: " + tn.read_until("MAGIC", timeout=5)
    return tn 

def lan_send(tn, command, verbose=False, wait=True):
    if wait:
        tn.write(command + ';*WAI\r\n')
    else:   
        tn.write(command + '\r\n')

    time.sleep(.05)
    response = tn.read_until('>', VNATIMEOUT)
    response = response[:-7] # strip trailing SCPI>\r\n
    if(verbose):
        print str(command) + ', reponse: ' + str(response)
    return response

def lan_close(tn):
    response = tn.read_very_lazy() # check if there is anything left in the buffer..
    if response != '':
        print 'uh oh.. we found something in the recieve buffer: ' + str(response)
    tn.close()

if __name__ == '__main__':
    tn = lan_init(VNAHOST)
    lan_close(tn)

import telnetlib
import time

VNATIMEOUT = 5  # seconds
NE5230APORT = 5024
VNAHOST = '192.168.11.3'


def lan_init(host, port=23):
    telnet_connection = telnetlib.Telnet(host, port)
    time.sleep(.5)
    print("initial response from VNA: " + telnet_connection.read_until("MAGIC", timeout=5))
    return telnet_connection


def lan_send(telnet_connection, command, verbose=False, wait=True):
    if wait:
        telnet_connection.write(command + ';*WAI\r\n')
    else:   
        telnet_connection.write(command + '\r\n')

    time.sleep(.05)
    response = telnet_connection.read_until('>', VNATIMEOUT)
    response = response[:-7]  # strip trailing SCPI>\r\n
    if verbose:
        print(str(command) + ', response: ' + str(response))
    return response


def lan_close(telnet_connection):
    response = telnet_connection.read_very_lazy()  # check if there is anything left in the buffer..
    if response != '':
        print('uh oh.. we found something in the receive buffer: ' + str(response))
    telnet_connection.close()


if __name__ == '__main__':
    tn = lan_init(VNAHOST, NE5230APORT)
    lan_close(tn)

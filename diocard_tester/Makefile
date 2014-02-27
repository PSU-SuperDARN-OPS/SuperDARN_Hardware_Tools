OS:=$(shell uname -s)

CC=gcc
CFLAGS=-B /usr/ -c
common_libs=-lm
qnx_libs=-lsocket
INCLUDES=-I"/usr/include/" -I"../include/" -I"include/" -I"../tsg/include"   

SOURCES=dio_self_test.c  _open_PLX9050.c _prog_conventions.c utils.c 
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=dio_self_test

all: $(SOURCES)

$(EXECUTABLE): $(OBJECTS)
	$(CC) -o $@ $(OBJECTS) $(common_libs) $(qnx_libs) 

.c.o:
	$(CC) $(CFLAGS) $(INCLUDES) $< -o $@ 

clean:
	rm -rf $(OBJECTS) $(EXECUTABLE)



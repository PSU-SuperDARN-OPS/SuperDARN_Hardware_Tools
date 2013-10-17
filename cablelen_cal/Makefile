OS:=$(shell uname -s)

CC=gcc
CFLAGS=-c
common_libs=-lm
linux_libs=
qnx_libs=-lsocket
INCLUDES=-I"include/"    

RF_SOURCES=rf_cal.c   utils.c 
RF_OBJECTS=$(RF_SOURCES:.c=.o)
RF_EXECUTABLE=rf_calibration


all: $(RF_SOURCES) $(RF_EXECUTABLE) 

$(RF_EXECUTABLE): $(RF_OBJECTS)
ifeq ($(OS),Darwin)
	$(CC) -o $@ $(RF_OBJECTS) $(common_libs) $(linux_libs) 
endif
ifeq ($(OS),Linux)
	 $(CC) -o $@ $(RF_OBJECTS) $(common_libs) $(linux_libs)
endif
ifeq ($(OS),QNX)
	$(CC) -o $@ $(RF_OBJECTS) $(common_libs) $(qnx_libs) 
endif

.c.o:
	$(CC) $(CFLAGS) $< -o $@ $(INCLUDES)

clean:
	rm -rf $(RF_EXECUTABLE) $(RF_OBJECTS)



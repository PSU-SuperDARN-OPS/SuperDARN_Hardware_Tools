OS:=$(shell uname -s)

CCpp=g++ -std=c++0x
CC=gcc
CFLAGS=-c -g3
common_libs=-lm -lrt -luhd -lfftw3 -lboost_system -lboost_thread -lboost_filesystem
INCLUDES=-I"." -I"/usr/include/boost"
CPP_SOURCES=main.cpp 
CPP_OBJECTS=$(CPP_SOURCES:.cpp=.o)

EXECUTABLE=dio_test

all: $(EXECUTABLE)

$(EXECUTABLE): $(CPP_OBJECTS)
	$(CCpp) -o $@ $(CPP_OBJECTS) $(linux_libs) $(common_libs)

.cpp.o:
	$(CCpp) $(CFLAGS) $< -o $@ -c $(INCLUDES) $(common_libs)

clean:
	rm -rf *.o dio_test 


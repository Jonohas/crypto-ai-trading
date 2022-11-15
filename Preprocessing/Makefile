# create CC variable
CC = gcc
# create CFLAGS variable

CFLAGS = -I/usr/local/include -Wall -g
LDFLAGS = -L/usr/local/lib
LDLIBS = -lta_lib -lm

output: main.c
	$(CC) $(LDFLAGS) $(CFLAGS) -o output main.c $(LDLIBS)

clean:
	rm -f *.o output
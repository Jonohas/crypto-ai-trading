# create CC variable
CC = gcc
# create CFLAGS variable

CFLAGS =  -Wall -g $(INCLUDES)

LDLIBS = -lta_lib -lm

output: main.o
	$(CC) $(LDLIBS) -o output main.o

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

# target: dependencies
# 		action

clean:
	rm -f *.o output
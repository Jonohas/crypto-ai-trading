# create CC variable
CC = gcc
# create CFLAGS variable

INCLUDES = -I/usr/local/lib -I/usr/local/include
CFLAGS =  -Wall -g $(INCLUDES)

LDFLAGS = -L/usr/local/lib -L/usr/local/include

output: main.o
	$(CC) $(LDFLAGS) -o output main.o

main.o: main.c
	$(CC) $(CFLAGS) -c main.c

# target: dependencies
# 		action

clean:
	rm -f *.o output
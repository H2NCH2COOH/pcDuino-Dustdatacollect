CC=gcc
CFLAGS=-c -Wall
LDFLAGS=

OBJS=main.o gpio.o
SRCS=main.c gpio.c
HDRS=gpio.h
EXEC=dust_data_collect_routine

all: $(EXEC)

$(EXEC): $(OBJS)
	$(CC) -o $@ $(OBJS)

%.o: %.c $(HDRS)
	$(CC) $(CFLAGS) -o $@ $<

clean:
	rm $(EXEC) $(OBJS)

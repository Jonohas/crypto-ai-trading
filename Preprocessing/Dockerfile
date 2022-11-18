FROM ubuntu:22.04

WORKDIR /app


RUN apt-get update && apt-get install -y make gcc wget
RUN wget https://sourceforge.net/projects/ta-lib/files/ta-lib/0.4.0/ta-lib-0.4.0-src.tar.gz
RUN tar -xzf ta-lib-0.4.0-src.tar.gz && cd ta-lib/ && ./configure && make && make install

COPY custom_ld.so.conf /etc/ld.so.conf
RUN /sbin/ldconfig


COPY main.c /app/main.c
COPY Makefile /app/Makefile

RUN make






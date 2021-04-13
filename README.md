# Custom Reliale Transport Protocol

> CMPT 371 - Project
> Spring 2021
> Auther: Hao Wu, Ross Shen

## Description

We have chosen option 2 for this Mini Project. As we studied and observed from
the TCP protocol behaviours, we adapted the main components of TCP to recreate
a connection-oriented and pipelined protocol for transmission between two hosts.
Our protocol is built on top of the UDP protocol, yet providing reliable
transportation with flow control, congestion control similar to the TCP protocol.
We have also provided interfaces to reliably transfer files from server to client
with multiple simultaneous clients supported.

## Protocol Design

### Transport Segment Structure

In our protocol, the header is placed in the first 16 bytes of the UDP payload,
and the data comes right after with a maximum size of 1024 bytes. We adapted the
header structure from the TCP protocol as shown below.

```
   0                   1                   2                   3
    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |          Source Port          |       Destination Port        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                        Sequence Number                        |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                    Acknowledgment Number                      |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                               |A|S|F|                         |
   |            Window             |C|Y|I|        padding          |
   |                               |K|N|N|                         |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
   |                             data                              |
   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### Three-way Handshaking

![handshaking](./README_src/handshaking.png)

### Connection Management

## Wireshark Analysis

We implemented connection orientation by applying the TCP’s 3 way handshake and
connection closure to ensure both hosts identify and allocate dedicated ports
for a pipelined transmission.

## Usage

- two ways for invoke client

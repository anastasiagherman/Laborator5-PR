#!/usr/bin/env python3
# coding: utf-8

import socket
import argparse

import video_grabber

jpeg_quality = 50
host = '127.0.0.1'
port = 10080
encoder = 'cv2'

# The grabber of the webcam
grabber = video_grabber.VideoGrabber(jpeg_quality, encoder)
grabber.start()
get_message = lambda: grabber.get_buffer()

keep_running = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = (host, port)

print('starting up on %s port %s\n' % server_address)

sock.bind(server_address)

while (keep_running):
    data, address = sock.recvfrom(4)
    data = data.decode('utf-8')
    if (data == "get"):
        buffer = get_message()
        if buffer is None:
            continue
        if len(buffer) > 65507:
            print(
                "The message is too large to be sent within a single UDP datagram. "
                "We do not handle splitting the message in multiple datagrams")
            sock.sendto("FAIL".encode('utf-8'), address)
            continue
        # We send back the buffer to the client
        sock.sendto(buffer, address)
    elif (data == "quit"):
        grabber.stop()
        keep_running = False

print("Quitting..")
grabber.join()
sock.close()

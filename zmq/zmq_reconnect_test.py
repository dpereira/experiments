"""Test to exercise reconnecting sockets.

This demonstrates how a dealer socket will
come back to send messages to a router socket,
after the event the router socket disconnects
and binds back again in the same port. Steps
for executing the test:

    1. Run the router: python zmq_reconnect_test.py router 10001
    2. Run the dealer, connecting to the router: python zmq_reconnect_test.py dealer 10001
    3. Interrupt the router (ctrl+c). Wait for a few seconds
    4. Re-run the router with the same commands used in step 1.
    5. Notice that the dealer sends many messages that were buffered, and resumes then sending them every second.
"""

import sys
import time
import zmq


def dealer(connection_port):
    context = zmq.Context()
    socket = context.socket(zmq.DEALER)
    socket.connect(f'tcp://localhost:{connection_port}')

    while True:
        socket.send(b'Hello')
        time.sleep(1)


def router(binding_port):
    context = zmq.Context()
    socket = context.socket(zmq.ROUTER)
    socket.bind(f'tcp://*:{binding_port}')

    while True:
        data = socket.recv()
        print(f'Received: {data}')

if __name__ == '__main__':
    mode = sys.argv[1]
    port = sys.argv[2]
    if sys.argv[1] == 'dealer':
        dealer(port)
    else:
        router(port)



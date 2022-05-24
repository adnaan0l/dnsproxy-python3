from asyncio.log import logger
import sys
import time
import logging
import threading
import traceback
import socketserver

import upstream_query
import config

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    """
    Class to handle DNS queries via TCP/TLS. 
    """

    def handle(self):
        tcp_logger = logging.getLogger("root.tcp_handler")
        tcp_logger.info("Received request for {} over TCP/TLS".format(self.client_address))

        try:
            query = self.request.recv(1024)
            params = ('tcp', config.dns_server, config.secure_udp, config.ca_path)
            answer = upstream_query.handler(query, params)
            self.request.sendall(answer)
        except Exception as e:
            tcp_logger.info('Failed to process request')
            tcp_logger.error(e)
            tcp_logger.error(traceback.print_exc())

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    """
    Class to handle DNS queries via UDP.
    """
    def handle(self):
        udp_logger = logging.getLogger("root.udp_handler")
        udp_logger.info("Received request for {} over UDP".format(self.client_address))
        
        try:
            query, socket = self.request
            params = ('udp', config.dns_server, config.secure_udp, config.ca_path)
            answer = upstream_query.handler(query, params)
            socket.sendto(answer, self.client_address)
        except Exception as e:
            udp_logger.info('Failed to process request')
            udp_logger.error(e)
            udp_logger.error(traceback.print_exc())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    """
    This creates a Threading TCP server which handles
    each DNS query over TCP/TLS in a seperate thread.
    """
    pass

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    """
    This creates a Threading UDP server which handles
    each DNS query via UDP in a seperate thread.
    """
    pass


if __name__ == "__main__":
    HOST, PORT = config.host_ip, config.daemon_port

    base_logger = logging.getLogger('root')

    servers = [
        ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler),
        ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    ]

    base_logger.info("Starting proxy daemon...")

    for server in servers:
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
    
    base_logger.info("Successfully started proxy daemon")
    base_logger.info("Listening on port {}".format(PORT))

    try:
        while 1:
            time.sleep(1)
            sys.stderr.flush()
            sys.stdout.flush()

    except KeyboardInterrupt:
        base_logger.info("Keyboard Interrupt received. Closing connections...")
        pass
    finally:
        for server in servers:
            server.shutdown()
        base_logger.info("Successfully shutdown proxy.")
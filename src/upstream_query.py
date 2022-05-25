import socket
import ssl
import logging
import binascii

client_logger = logging.getLogger("root.clients")

def _send_request_tls(proto, query, dns_server, ca_path):
    """ 
    Method to query DNS over TCP secured with TLS.
    Returns the server response.
    """
    try:
        server = (dns_server, 853)

        # create a ssl context with the TLS protocol
        # requiring peer certificate verification through a set of loaded CA certs
        # requiring a peer hostname check
        ssl_ctx = ssl.create_default_context()
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.check_hostname = True
        ssl_ctx.load_verify_locations(ca_path)

        # create a tcp socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(60)
        
            # wrapping the tcp socket in the configured ssl context
            with ssl_ctx.wrap_socket(sock, server_hostname=dns_server) as ssock:
                ssock.connect(server)

                # query upstream dns server over a ssl wrapped tcp socket
                if proto == 'tcp':
                    ssock.sendall(query)
                elif proto == 'udp':
                    tcp_msg = "\x00".encode() + chr(len(query)).encode() + query
                    ssock.send(tcp_msg)
    except:
        raise
    else:
        return ssock.recv(1024)
    finally:
        client_logger.info("Closing connection...")
        ssock.close()

def _send_request_udp(dns_server, query):
    """ 
    Method to query DNS over UDP.
    Returns the server response.
    """
    try:
        HOST, PORT = (dns_server, 53)

        # query upstream dns server over a udp socket on port 53
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(5)
            sock.sendto(query, (HOST, PORT))
    except:
        raise
    else:
        return sock.recv(1024)
    finally:
        sock.close()

def _get_rcode(proto, secure_udp, answer):
    """ 
    Method to check DNS response RCODES.
    Logs the RCODE.
    Returns the server response. 
    """
    if answer:
        try:
            if (proto == 'tcp') or (proto=='udp' and secure_udp):
                rcode = binascii.hexlify(answer[:6]).decode("utf-8")
                rcode = rcode[11:]
            elif (proto == 'udp' and not secure_udp):
                rcode = binascii.hexlify(answer[:4]).decode("utf-8")
                rcode = rcode[7:]

            if int(rcode, 16) == 0:
                client_logger.info("Query Successful. RCODE = %s", rcode)
            else:
                client_logger.error("Error processing the request. RCODE = %s",rcode)

            if (proto=='udp' and secure_udp):
                return answer[2:]
            else:
                return answer

        except:
            raise
    else:
        client_logger.warn("Query Failed. Empty reply from server")

def handler(query, params):
    """
    Main handler to manage DNS queries over TCP or UDP.
    Returns the server response.
    """
    proto, dns_server, secure_udp, ca_path = params

    if (proto == 'tcp') or (proto=='udp' and secure_udp):
        answer = _send_request_tls(proto, query, dns_server, ca_path)
    elif (proto == 'udp' and not secure_udp):
        answer = _send_request_udp(dns_server, query)
    else:
        client_logger.error('Invalid value for Proto')
        pass

    return _get_rcode(proto, secure_udp, answer)

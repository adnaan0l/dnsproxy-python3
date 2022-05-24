import socket
import ssl
import logging
import binascii

client_logger = logging.getLogger("root.clients")

def _send_request_tls(proto, query, dns_server, ca_path):
    """ 
    Method to query DNS over TCP secured with TLS
    """
    try:
        server = (dns_server, 853)  # default port for cloudflare

        # tcp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(60)

        ssl_ctx = ssl.create_default_context()
        ssl_ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        ssl_ctx.verify_mode = ssl.CERT_REQUIRED
        ssl_ctx.check_hostname = True
        print(ca_path)
        ssl_ctx.load_verify_locations(ca_path)

        wrapped_socket = ssl_ctx.wrap_socket(sock, server_hostname=dns_server)
        wrapped_socket.connect(server)

        if proto == 'tcp':
            wrapped_socket.sendall(query)
        elif proto == 'udp':
            tcp_msg = "\x00".encode() + chr(len(query)).encode() + query
            wrapped_socket.send(tcp_msg)
    except:
        raise
    else:
        answer = wrapped_socket.recv(1024)
        return answer
    finally:
        client_logger.info("Closing connection...")
        wrapped_socket.close()

def _send_request_udp(dns_server, query):
    """ 
    Method to query DNS over UDP
    """
    try:
        HOST, PORT = (dns_server, 53)

        # udp socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        sock.sendto(query, (HOST, PORT))
        answer = sock.recv(1024)
        return answer
    except:
        raise
    finally:
        sock.close()

def _get_rcode(proto, secure_udp, answer):
    """ Method to check DNS response RCODES """
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
    Main handler to manage DNS queries over TCP or UDP
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

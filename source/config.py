import logging
import sys
import json
import argparse

""" Cache Initialization """
cache = {}

""" Base params initialization """
parser = argparse.ArgumentParser(description='Setup a simple DNS daemon')
parser.add_argument('--dns-server', type=str, choices=['cloudflare', 'google'], help='Upstream DNS Server to query. Default=1.0.0.1', default='1.0.0.1')
parser.add_argument('--secure-udp', type=str , choices=['true', 'false'], help='Option to secure DNS queries over UDP. Default=true', default='true')
args = parser.parse_args()

""" Read json config"""
with open('params.json') as f:
   params = json.load(f)

""" Set SSL certificate path"""
ca_path = params.get('ca-path')

""" DNS server to use """
if args.dns_server in params.get('dns-servers'):
    dns_server = params.get('dns-servers').get(args.dns_server)
else:
    dns_server = params.get('dns-servers').get('default')

""" Set UDP secure config """
if args.secure_udp == 'false':
    secure_udp = False
else:
    secure_udp = True

""" Set Host IP """
host_ip = params.get('host-ip')

""" Set Daemon port """
daemon_port = params.get('daemon-port')

""" Logging Config """
info_handler = logging.FileHandler(filename='logs/info.log')
error_handler = logging.FileHandler(filename='logs/error.log')
stdout_handler = logging.StreamHandler(sys.stdout)

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} - THREAD_ID:%(thread)d - %(levelname)s - %(message)s',
    handlers=[info_handler, stdout_handler] 
)

logging.basicConfig(
    level=logging.WARN, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} - THREAD_ID:%(thread)d - %(levelname)s - %(message)s',
    handlers=error_handler
)

# Simple DNS over TLS daemon  

Simple daemon that listens to DNS queries made to udp/53 and tcp/53.
Redirects to a DNS server that supports TLS over an encrypted channel for privacy.
Works over plain-text if requred. (by setting)
Runs using multithreaded servers and accept multiples requests.

## Requirements
* Python3
* Docker

## Usage

  Build the image using the Dockerfile
  ```
  $ docker build -t="dnstls" .
  $ docker run --rm -p 53:53/tcp -p 53:53/udp dnstls
  ```
  
  You may set new values for configuration (dns server, secure-udp) using the
  flags options.
  
  Options:
  -  --dns-server TEXT  Upstream DNS server to query -   [default: 1.0.0.1]
  -  --secure-udp TEXT  Option to send UDP queries over TLS instead of in plain-text [default: true]
  
  Example:
  ```
  docker run --rm -p 53:53/tcp -p 53:53/udp dnstls --dns-server=cloudflare --secure-udp=true
  ```

## Testing
  After start the proxy, you can test a DNS request using Dig.
  Query using UDP:
  ```
  $ dig @127.0.0.1 google.com
  ```
  Query using TCP:
  ```
  $ dig @127.0.0.1 google.com +tcp
  ```
  For multiple requests, run from project root 
  ```
  ./tests/queryflood.sh 
  ```
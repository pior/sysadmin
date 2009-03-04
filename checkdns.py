#!/usr/bin/env python

"""Check a list of hostnames against a list of dns servers

Return 0 if all hostnames resolved well from all dns servers
Return 1 otherwise

Install:
    centos:
        add rpmforge repo
        yum install python-dns
    debian/ubuntu:
        apt-get install python-dnspython

Note on multiple ip record:
    A hostname resolve well if at least one of the IPs match
    the expected IP.
"""

dnsserver = dict()
hostname = dict()
################### CONFIG #####################

dnsserver['opendns'] = '208.67.222.222'
dnsserver['level3'] = '4.2.2.1'
dnsserver['free.fr'] = '212.27.40.241'
dnsserver['neuf'] = '212.30.96.108'

hostname['example.com'] = '208.77.188.166'
hostname['endoftheinternet.com'] = '66.146.2.196'

################### END OF CONFIG ################



############ DO NOT CROSS THIS LINE ##############

import sys
import dns.resolver
from threading import Thread
import logging

logging.basicConfig(level=logging.DEBUG)

class resolverthread(Thread):
    def __init__ (self, name, server, joblist):
        Thread.__init__(self)
        self.joblist = joblist
        self.name = name
        self.server = server
        self.result = dict()
        self.error = False

    def run(self):
        logging.info('Thread[%s] starting...' % (self.name))
        import dns.resolver
        R = dns.resolver.Resolver(configure=False)
        R.nameservers = [self.server]
        R.lifetime = 5
        dns.resolver.default_resolver = R
        for host in self.joblist:
            try:
                answer = dns.resolver.query(host)
            except dns.resolver.NoAnswer:
                self.result[host] = None
            except dns.resolver.Timeout:
                logging.error('Timeout when waiting for %s (%s)' % (self.name, self.server))
                self.error = True
                break
            else:
                self.result[host] = [h.address for h in answer.rrset]
            logging.info('Thread[%s] host=%s result=%s' % (self.name, host, str(self.result[host])))

def main():
    workers = []
    error = False
    # Launch the threads
    for dsname, dsaddr in dnsserver.iteritems():
        logging.info('Start thread for dns server %s' % dsname)
        worker = resolverthread(dsname, dsaddr, hostname.keys())
        workers.append(worker)
        worker.start()
    # Wait and check the result
    for worker in workers:
        worker.join()
        if worker.error:
            error = True
            continue
        for host, addr in hostname.iteritems():
            if addr not in worker.result[host]:
                logging.error('%s is %s and should be %s on %s' % (host, str(worker.result[host]), addr, worker.server))
                error = True
    sys.exit(error)

if __name__ == "__main__":
    main()


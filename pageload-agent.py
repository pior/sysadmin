#!/usr/bin/env python

import pycurl
import sys

if not len(sys.argv) == 3:
    sys.exit("%s URL HOST" % sys.argv[0])

argurl = sys.argv[1]
arghost = sys.argv[2]

argurl = argurl.split('/')

url = "/".join([argurl[0],argurl[1],arghost] + argurl[3:])
host = argurl[2]

c = pycurl.Curl()

c.setopt(pycurl.URL, url)
c.setopt(pycurl.HTTPHEADER, ["Host: %s" % host])
import StringIO
b = StringIO.StringIO()
c.setopt(pycurl.WRITEFUNCTION, b.write)
c.setopt(pycurl.FOLLOWLOCATION, 0)
c.perform()

if c.getinfo(pycurl.HTTP_CODE) < 400:
    print "dns:%s con:%s pre:%s str:%s ttl:%s sze:%s spd:%s" % (
        c.getinfo(pycurl.NAMELOOKUP_TIME),
        c.getinfo(pycurl.CONNECT_TIME),
        c.getinfo(pycurl.PRETRANSFER_TIME),
        c.getinfo(pycurl.STARTTRANSFER_TIME),
        c.getinfo(pycurl.TOTAL_TIME),
        c.getinfo(pycurl.SIZE_DOWNLOAD),
        c.getinfo(pycurl.SPEED_DOWNLOAD) )

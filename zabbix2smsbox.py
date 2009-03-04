#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pior Bastida
# License: Public domain code

import os
import sys
import logging

from smsbox import smsbox, SmsboxapiError

# Check the permission !
logfile = '/var/log/zabbix/alert.log'

# The smsbox account (password can be in clear or md5 hexdigest)
username = 'REPLACEME'
password = 'REPLACEME'

# using https ?
secure = True

# send classic sms or flash sms ?
smsflashmode = True

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit(u'This script need to be called by zabbix with 3 arguments')

    recipient = sys.argv[1]
    subject = sys.argv[2]
    body = sys.argv[3]

    # Start the logger engine, full speed !
    try:
        logger = logging.getLogger(sys.argv[0])
        hdlr = logging.FileHandler(logfile)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.INFO)
    except IOError:
        sys.exit(u"Can't write in %s. Check permission." % logfile)

    # First we take manhatten...
    logger.info('Called with rcpt="%s" subject="%s" body="%s"' % (recipient, subject, body))

    try:
        # Send message
        logger.debug('Init smsbox with user="%s" password="%s" secure="%s"' % (username, password, secure))
        smsapi = smsbox(user=username, password=password, secure=secure)
        try:
            message = subject.strip('\n ').replace('\n', ' ')
            if len(message) > 160:
                message = message[0:160]
                logger.warning('Message larger than 160 chars. Troncated')
            logger.debug('Sending sms with msg="%s" dest="%s" flash="%s"' % (message, recipient, smsflashmode))
            smsapi.send(msg=message, dest=recipient, flash=smsflashmode)
        except SmsboxapiError, e:
            logger.error('Error while sendind message. %s' % str(e))
            sys.exit(1)
    except Exception, e:
        logger.exception('Stopped with error.')
        sys.exit(1)

    logger.info('Stopped without error')
    sys.exit(0)

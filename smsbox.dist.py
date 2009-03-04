#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pior Bastida
# License: Public domain code

import os
import sys
import urllib
import urllib2
import socket

class SmsboxapiError(IOError):
    pass

class smsbox(object):
    """smsbox(user=None, password=None, secure=False)"""
    def __init__(self, user=None, password=None, secure=False):
        if not user or not password:
            raise ValueError('Need a username and a password')
        self._user = user
        self._pass = password
        self._query = 'http%s://api.smsbox.fr/api.' % (secure and 's' or '')
        socket.setdefaulttimeout(10)

    def _request(self, param, rsptype='php', debug=False):
        if not rsptype in ['xml','php']:
            raise ValueError('rsptype need te be xml or php')
        param['login'] = self._user
        param['pass'] = self._pass
        data = urllib.urlencode(param)
        if debug:
            print 'The post data is "%s"' % data
            print 'The url is "%s%s"' % (self._query, rsptype)
        req = urllib2.Request(self._query + rsptype, data)
        try:
            handle = urllib2.urlopen(req)
        except IOError, e:
            if hasattr(e, 'reason'):
                raise SmsboxapiError("Can't reach the server. Reason: %s" % e.reason)
            elif hasattr(e, 'code'):
                raise SmsboxapiError("The server returned an error. Error code: %s" % e.code)
            raise SmsboxapiError('Error while http request')
        return handle.read()

    def _parse(self, response, tag=None, split=True):
        """Only for PHP api"""
        response = response.strip('\n ')
        for line in response.split('\n'):
            if line.startswith('ERROR'):
                raise SmsboxapiError('SmsBox api returned: "%s"' % line)
            if split:
                args = line.split(' ', 1)
                if len(args) == 1:
                    args.append('')
                if not tag or len(tag) == 0 or tag == args[0]:
                    yield [args[0], args[1]]
            else:
                yield line

    def credit(self):
        """credit(self)"""
        param = {'action' : 'credit'}
        response = self._request(param)
        for credit in self._parse(response, 'CREDIT'):
            return float(credit[1])
        return None

    def send(self, msg=None, dest=None, orig=None, flash=False, response=False, multi=False, callback=False):
        """send(self, msg=None, dest=None, orig=None, flash=False, response=False, multi=False, callback=False)"""
        if not dest or not len(dest):
            raise ValueError("No destination specified")
        if not msg or not len(msg):
            raise ValueError("No message specified")
        if (flash and orig) or (flash and response) or (response and orig):
            raise ValueError("You can specify only one option at a time")
        param = {   'mode': 'Economique',
                    'type': '0',
                    'udh': '0',
                    'id': '1',
                    'callback': '0'}
        if flash:
            param['type'] = '1'
        if orig:
            param['mode'] = 'Expert'
            param['origine'] = orig
        if response:
            param['mode'] = 'Reponse'
        param['dest'] = dest
        param['msg'] = msg
        response = self._request(param, debug=False)
        for rep in self._parse(response, 'OK'):
            return rep[1].split(',')
        return None

    def _status(self, sms):
        statustext = {  -3:u'SMS recrédité',
                        -2:u'En attente d\'envoi',
                        -1:u'Statut inconnu',
                        0:u'Message reçu',
                        1:u'Échec de la transmission',
                        2:u'Message rejeté',
                        3:u'Mobile de destination inactif',
                        4:u'Mobile de destination ne répond pas',
                        5:u'Erreur lors de la réception',
                        6:u'Mobile de destination saturé',
                        7:u'Numéro de destination inconnu',
                        8:u'Message non-routable',
                        9:u'Message transmis',
                        10:u'Message envoyé' }
        # here, error means that the msg will probably
        # not be delivred without actions
        statuserror = [-3, -1, 1, 2, 3, 4, 5, 6, 7, 8]
        d = sms.split(';')
        data = {}
        data['date'] = d[0].split(' ')[0]
        data['time'] = d[0].split(' ')[1]
        data['dest'] = d[1]
        data['orig'] = d[2]
        data['type'] = int(d[3])
        data['methode'] = int(d[4])
        data['status'] = int(d[5])
        data['longstatus'] = statustext[data['status']]
        data['error'] = data['status'] in statuserror
        return data

    def _getstatus(self, param):
        if not id or not id > 0:
            raise ValueError("No message ID specified")
        param['action'] = 'historique'
        response = self._request(param, debug=False)
        smss = self._parse(response, split=False)
        for sms in smss:
            yield self._status(sms)

    def _getlog(self):
        param = {'action': 'historique'}
        response = self._request(param, debug=False)
        for hist in self._parse(response, tag='HISTORIQUE'):
            return int(hist[1])
        return None

    def getstatusid(self, id):
        """getstatusid(self, id)"""
        param = {'id': id}
        for st in self._getstatus(param):
            return st
        return None

    def getstatusall(self, limit=False):
        """getstatusall(self, limit=False)"""
        nsms = self._getlog()
        nb = limit and min(nsms, limit) or nsms
        param = {   'from': str(nsms - nb),
                    'nb': str(nb)}
        statusgene = self._getstatus(param)
        return statusgene

    def getstatusdate(self, datefrom, dateto):
        """The date format is YYYY-MM-DD"""
        param = {   'date_from': datefrom,
                    'date_to': dateto}
        statusgene = self._getstatus(param)
        return statusgene

    def status2str(self, status):
        s = "%(date)s-%(time)s from=%(orig)11s to=%(dest)11s status=%(longstatus)s" % status
        return s


def example():
    print "You need to modify the pasword field"
    smsapi = smsbox(user='pior', password='', secure = True)
    print smsapi.credit()
    print s.send(msg='test', orig=None, dest='0688694770', flash=False, response=False)
    print smsapi.getstatusid(80803430820).items()
    for st in smsapi.getstatusall(limit=10):
        print "Sent at %s : %s" % (st['time'],st['longstatus'])


if __name__ == '__main__':
    try:
        import optparse
        # Parse command line
        parser = optparse.OptionParser(
                usage='Usage: %prog [options] ACTION...',
                version='2008.08.04',
                conflict_handler='resolve',
                description="ACTION can be: CREDIT SEND SENDFLASH SENDFROM STATUS STATUSALL")
        parser.add_option('-h', '--help',
                action='help', help='print this help text and exit')
        parser.add_option('-v', '--version',
                action='version', help='print program version and exit')
        parser.add_option('-u', '--username',
                dest='username', metavar='UN', help='account username')
        parser.add_option('-p', '--password',
                dest='password', metavar='PW', help='account password')
        parser.add_option('-s', '--secure',
                action='store_true', dest='secure', help='use https', default=False)
        parser.add_option('-q', '--quiet',
                action='store_true', dest='quiet', help='activates quiet mode', default=False)
        (opts, args) = parser.parse_args()

        # Conflicting, missing and erroneous options
        if len(args) < 1:
            parser.error(u'you must specified an action')
        if opts.password is None or opts.username is None:
            parser.error(u'account username and password missing')

        action = args[0].lower()

        if action == 'credit':
            smsapi = smsbox(user=opts.username, password=opts.password, secure=opts.secure)
            credit = smsapi.credit()
            if opts.quiet:
                print credit
            else:
                print "You have %s credit%s left." % (credit, credit>=2 and 's' or '')
            sys.exit(not credit)

        elif action in ['send','sendflash']:
            if len(args) < 3:
                parser.error(u'you must at least specified a recipient and a message')
            rcpt = args[1]
            msg = args[2]
            smsapi = smsbox(user=opts.username, password=opts.password, secure=opts.secure)

            try:
                ret = smsapi.send(msg=msg, dest=rcpt, flash = (action=='sendflash') )
            except SmsboxapiError, e:
                print e
                sys.exit(u'Error while sending the message')
            if not opts.quiet:
                print "The message has been sent. ID=%s" % ret

        elif action == 'sendfrom':
            if len(args) < 4:
                parser.error(u'you must at least specified an origin, a recipient and a message')
            orig = args[1]
            rcpt = args[2]
            msg = args[3]
            smsapi = smsbox(user=opts.username, password=opts.password, secure=opts.secure)
            try:
                ret = smsapi.send(msg=msg, orig=orig, dest=rcpt)
            except SmsboxapiError, e:
                print e
                sys.exit(u'Error while sending the message')
            if not opts.quiet:
                print "The message has been sent. ID=%s" % ret

        elif action == 'statusall':
            smsapi = smsbox(user=opts.username, password=opts.password, secure=opts.secure)
            for st in smsapi.getstatusall():
                print smsapi.status2str(st)

        elif action == 'status':
            if len(args) < 2:
                parser.error(u'you must specified the message ID')
            id = args[1]
            smsapi = smsbox(user=opts.username, password=opts.password, secure=opts.secure)
            st = smsapi.getstatusid(id)
            if opts.quiet:
                print st['error'] and 'ERROR' or 'OK'
            else:
                print smsapi.status2str(st)

        else:
            if not opts.quiet:
                parser.error(u'this action is not supported. Try --help.')
            sys.exit(2)

    except KeyboardInterrupt:
        sys.exit(u'\nERROR: Interrupted by user')


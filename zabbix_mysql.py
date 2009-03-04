#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pior Bastida
# License: Public domain code

import os
import sys
import popen2

user = 'REPLACEME'
password = 'REPLACEME'

def run(cmd):
    mysql_cmd = "mysql -u%s -p%s -Bse '%%s'" % (user, password)
    p = popen2.Popen4(mysql_cmd % cmd)
    rc = p.wait()
    out = p.fromchild.read()
    return (rc, out)

def get_server_status():
    rc, out = run("show status;")
    if not rc == 0:
        raise IOError('mysql returned %s' % rc)
    state = {}
    for line in out.split('\n'):
        data = line.strip().split('\t')
        if len(data) == 1:
            state[data[0]] = ''
        if len(data) == 2:
            state[data[0]] = data[1]
    return state

def server_ping():
    rc, out = run("select 42;")
    if not rc == 0:
        return False
    for line in out.split('\n'):
        if line.strip().startswith('42'):
            return True
    return False

def get_slave_status():
    rc, out = run('show slave status\G')
    if not rc == 0:
        raise IOError('mysql returned %s' % rc)
    state = {}
    for line in out.split('\n'):
        data = line.strip().split(':')
        if len(data) == 1:
            state[data[0].strip()] = ''
        if len(data) == 2:
            state[data[0].strip()] = data[1].strip()
        if line.strip().startswith('Slave_IO_Running'):
            state['slaveiorunning'] = line.split(':')[1].strip()
        if line.strip().startswith('Slave_SQL_Running'):
            state['slavesqlrunning'] = line.split(':')[1].strip()
        if line.strip().startswith('Seconds_Behind_Master'):
            state['secondsbehindmaster'] = line.split(':')[1].strip()
    return state

def main():
    try:
        for arg in sys.argv:
            if arg == '--replication-running':
                state = get_slave_status()
                cond = state['Slave_IO_Running'] == "Yes"
                cond = cond and state['Slave_SQL_Running'] == "Yes"
                print cond and "1" or "0"
                sys.exit()
            if arg == '--replication-delay':
                state = get_slave_status()
                print state['Seconds_Behind_Master']
                sys.exit()
            if arg == '--questions':
                state = get_server_status()
                print state['Questions']
                sys.exit()
            if arg == '--slow-query':
                state = get_server_status()
                print state['Slow_queries']
                sys.exit()
            if arg == '--uptime':
                state = get_server_status()
                print state['Uptime']
                sys.exit()
            if arg == '--thread':
                state = get_server_status()
                print state['Threads_running']
                sys.exit()
            if arg == '--ping':
                ping = server_ping()
                print ping and "1" or "0"
                sys.exit()
    except IOError:
        print('0')
        sys.exit()
    s  = "Options are:\n  --replication-running\n  --replication-delay\n"
    s += "  --questions\n  --uptime\n  --slow-query\n  --thread\n"
    s += "  --ping\n"
    print('0')
    sys.exit(s)


if __name__ == "__main__":
    main()


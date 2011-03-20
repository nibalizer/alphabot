#!/usr/bin/env python

import os

cmdlist = ['add', 'remove', 'help', 'list', 'source']
log = './trip.log'
file = None

def add(msg):
    line = ' '.join(msg.rsplit()[1:])
    file.write(line + '\n')
    return 'added ' + '"' + line + '"'

def remove(msg):
    return 'in remove'

def help(msg):
    return 'work in progress, doing add, list, source. working on remove and others.'

def list():
    if file.tell():
        file.seek(0, 0)

    lines = file.readlines()
    lines = [l[:-1] for l in lines]

    return ' | '.join(lines)

def source():
    return 'source available at https://github.com/stutterbug/trailbot'

def dispatch(user, channel, msg):
    line = ''
    global file

    if msg[0] == '@':
        msg = msg[1:]
        cmd = msg.rsplit()[0]

        if os.path.exists(log):
            file = open(log, 'a+')
        else:
            file = open(log, 'w+')

        if cmd not in cmdlist:
            line = 'command not implemented'
        elif cmd in cmdlist[:3]:
            line = globals()[cmd](msg)
        elif cmd in cmdlist[3:]:
            line = globals()[cmd]()

        file.close()

    elif msg.startswith('trailbot'):
        line = 'prefix commands with "@"'

    return line

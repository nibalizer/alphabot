#!/usr/bin/env python

import os, fileinput as fi

cmdlist = ['add', 'remove', 'help', 'list', 'source']
log = './trip.log'
testlog = './test.log'
past = './past.log'
file = None

def getcontents():
    if file.tell():
        file.seek(0, 0)

    lines = file.readlines()
    lines = [l[:-1] for l in lines]
    return lines

def add(args):
    file.write(args + '\n')
    return 'added "' + args + '"'

def remove(args):
    result = ''
    trips = getcontents()
    match = filter(lambda e: args in e, trips)

    if len(match) == 0:
        result = 'no matching trips found'
    else:
        todel = match[0] + '\n'
        for line in fi.input(log, inplace=1):
            if line != todel: 
                print line,
        result = 'removed "' + match[0] + '"'
                
    return result

def help(args):
    return 'good: add, remove, list, source, help | soon: edit, comp, past, sorting, better help'

def list():
    tolist = getcontents()
    
    if len(tolist) > 0:
        first = 'the next trip is "' + tolist[0] + '", sending the full list in a pm'
        tolist.insert(0, first)

    return tolist

def source():
    return 'source available at https://github.com/stutterbug/trailbot'

def dispatch(user, channel, msg):
    reply = None
    global file

    if msg[0] == '@':
        msg = msg[1:]
        cmd = msg.rsplit()[0]
        args = ' '.join(msg.rsplit()[1:])

        if cmd == 'test':
            cmd = msg.rsplit()[1]
            args = ' '.join(msg.rsplit()[2:])

            if os.path.exists(testlog):
                file = open(testlog, 'a+')
            else:
                file = open(testlog, 'w+')
        else:
            if os.path.exists(log):
                file = open(log, 'a+')
            else:
                file = open(log, 'w+')

        if cmd not in cmdlist:
            reply = 'command not implemented'
        elif cmd in cmdlist[:3]:
            reply = globals()[cmd](args)
        elif cmd in cmdlist[3:]:
            reply = globals()[cmd]()

        file.close()
    elif msg.startswith('trailbot'):
        reply.append('prefix commands with "@"')
    else:
        reply = ''

    return reply

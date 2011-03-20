#!/usr/bin/env python

import os, re

cmdlist = ['add', 'remove', 'help', 'list', 'source']
log = './trip.log'
context = None
file = None

def getcontents():
    if file.tell():
        file.seek(0, 0)

    lines = file.readlines()
    lines = [l[:-1] for l in lines]
    return lines

def add(args):
    file.write(line + '\n')
    return ['added ' + '"' + line + '"']

def remove(args):
    result = []
    trips = getcontents()
    match = filter(lambda e: args in e, trips)
    
    if len(match) == 0:
        result.append('no matching trips found')
    else:
        result.extend(match[:1])

    return result

def help(args):
    return ['work in progress, doing add, list, source. working on remove and others.']

def list():
    tolist = getcontents()
    # use context for listing all in pm

    return tolist

def source():
    return ['source available at https://github.com/stutterbug/trailbot']

def dispatch(user, channel, msg, where):
    reply = []
    global context
    global file
    context = where

    if msg[0] == '@':
        msg = msg[1:]
        cmd = msg.rsplit()[0]
        args = ' '.join(msg.rsplit()[1:])

        if os.path.exists(log):
            file = open(log, 'a+')
        else:
            file = open(log, 'w+')

        if cmd not in cmdlist:
            reply.append('command not implemented')
        elif cmd in cmdlist[:3]:
            reply.extend(globals()[cmd](args))
        elif cmd in cmdlist[3:]:
            reply.extend(globals()[cmd]())

        file.close()

    elif msg.startswith('trailbot'):
        reply.append('prefix commands with "@"')

    return reply

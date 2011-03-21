#!/usr/bin/env python

import os, re, fileinput as fi

cmdlist = ['add', 'remove', 'edit', 'help', 'list', 'source']
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
        for line in fi.input(file.name, inplace=1):
            if line != todel: 
                print line,
        result = 'removed "' + match[0] + '"'
                
    return result

def edit(args):
    result = ''
    trips = getcontents()

    search = args.rsplit()[0]
    command = ' '.join(args.rsplit()[1:])

    form = re.search(r'^s/.*/.*/$', command)
    if not form:
        result = 'edit commands need the form: trip s/old/new/'
    else:
        old = command.split('/')[1]
        new = command.split('/')[2]
        match = filter(lambda e: search in e, trips)
        
        if len(match) == 0:
            result = 'no matching trips found'
        else:
            toedit = match[0] + '\n'
            edited = ''
            for line in fi.input(file.name, inplace=1):
                if line == toedit:
                    edited = line.replace(old, new, 1)
                    print edited,
                else:
                    print line,

            result = 'changed "' + match[0] + '" to "' + edited[:-1] + '"'
                
    return result    

def help(args):
    return 'good: add, remove, edit, list, source, help | soon: comp, past, sorting, better help'

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
        elif cmd in cmdlist[:4]:
            reply = globals()[cmd](args)
        elif cmd in cmdlist[4:]:
            reply = globals()[cmd]()

        file.close()
    elif msg.startswith('trailbot'):
        reply.append('prefix commands with "@"')
    else:
        reply = ''

    return reply

#!/usr/bin/env python
#
# ABQIAAAAAX65p8doZAZ2sD27O8hGxRRsaZwSbRsXRPeXpEJl89c2a4Dt3xTCoPsHXlv4iZnwZLg2C929GudycQ

from dateutil import parser
import os, re, fileinput as fi

cmdlist = ['add', 'remove', 'edit', 'comp', 'help', 'attending', 'missing', 'list', 'past', 'source']
magicnumber = 7
log = './trip.log'
pastlog = './past.log'
testlog = './test.log'
testpastlog = './testpast.log'
file = None

def getcontents(f):
    if f.tell():
        f.seek(0, 0)

    lines = f.readlines()
    lines = [l[:-1] for l in lines]
    return lines

def sorttrips(list):
    dated = []
    undated = []
    sortdict = {}

    for e in list:
        if re.search(r'(^|\s)[0-9][0-9]?/[0-9][0-9]?($|\s|,|\.|\?|!)', e):
            dated.append(e)
        else:
            undated.append(e)

    dates = [parser.parse(x, fuzzy=True) for x in dated]

    for x in range(len(dates)):
        sortdict[dates[x]] = dated[x]

    dates.sort(key = lambda x: x.timetuple()[1:3])
    dated = [sortdict[x] for x in dates]

    return dated + undated

def add(args):
    if args == '':
        return ''

    file.write(args + '\n')
    return 'added "' + args + '"'

def remove(args):
    response = ''
    trips = getcontents(file)

    if args == '':
        return response

    match = filter(lambda e: args in e, trips)

    if len(match) == 0:
        response = 'no matching trips found'
    else:
        todel = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line != todel: 
                print line,
        response = 'removed "' + match[0] + '"'
        fil.close()
    return response

def edit(args):
    response = ''
    trips = getcontents(file)
    cmdindex = 0

    if args == '':
        return response

    args = args.rsplit()
    for e in args:
        if 's/' in e:
            cmdindex = args.index(e)
            break

    search = ' '.join(args[:cmdindex])
    command = ' '.join(args[cmdindex:])

    form = re.search(r'^s/.*/.*/$', command)
    if not form:
        response = 'edit commands need the form: <keys> <s/old/new/>'
    else:
        old = re.split(r'(?<!\\)/', command)[1]
        new = re.split(r'(?<!\\)/', command)[2]

        if '\/' in old:
            old = old.replace('\/', '/')
        if '\/' in new:
            new = new.replace('\/', '/')

        match = filter(lambda e: search in e, trips)
        
        if len(match) == 0:
            response = 'no matching trips found'
        else:
            toedit = match[0] + '\n'
            edited = ''
            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == toedit:
                    edited = line.replace(old, new, 1)
                    print edited,
                else:
                    print line,
            fil.close()
            response = 'changed "' + match[0] + '" to "' + edited[:-1] + '"'
                
    return response    


def attending(args):
    response = ''
    trips = getcontents(file)
    if len(args) > 1:
        user = args[0]
        args = args[1]

    if args == '':
        return response

    match = filter(lambda e: args in e, trips)

    if len(match) == 0:
        response = 'no matching trips found'
    else:
        hasatt = True
        attindex = 0
        match = match[0].rsplit()
        for e in match:
            if '|attending|' in e:
                attindex = match.index(e)

        if attindex == 0:
            hasatt = False

        if hasatt and user in match[attindex:]:
            response = 'appreciate the enthusiasm, but you already said you would go' 
        else:
            match = ' '.join(match)
            toattend = match + '\n'
            attending = ''

            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == toattend:
                    if hasatt:
                        attending = line[:-1] + ' ' + user + '\n'
                        print attending,
                    else:
                        attending = line[:-1] + ' |attending| ' + user + '\n'
                        print attending,
                else:
                    print line,
            fil.close()
            response = user + ' is now attending "' + attending[:-1] + '"' 
                    
    return response

def missing(args):
    response = ''
    trips = getcontents(file)
    if len(args) > 1:
        user = args[0]
        args = args[1]

    if args == '':
        return response

    match = filter(lambda e: args in e, trips)

    if len(match) == 0:
        response = 'no matching trips found'
    else:
        hasatt = True
        attindex = 0
        match = match[0].rsplit()
        for e in match:
            if '|attending|' in e:
                attindex = match.index(e)

        if attindex == 0:
            hasatt = False

        if not hasatt:
            response = "no one is going yet" 
        elif user not in match[attindex:]:
            response = "you aren't attending yet" 
        else:
            match = ' '.join(match)
            tomiss = match + '\n'
            missing = ''

            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == tomiss:
                    start = line.rsplit('|attending|')[0]
                    finish = line.rsplit('|attending|')[1].rsplit()

                    if len(finish) == 1:
                        missing = start[:-1] + '\n'
                        print missing,
                    else:
                        finish.remove(user)
                        missing = start + '|attending| ' + ' '.join(finish) + '\n'
                        print missing,
                else:
                    print line,
            fil.close()
            response = user + ' is now missing "' + missing[:-1] + '"' 

    return response

def comp(args):
    response = ''
    trips = getcontents(file)

    if args == '':
        return response

    match = filter(lambda e: args in e, trips)

    if len(match) == 0:
        response = 'no matching trips found'
    else:
        tocomp = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line == tocomp:
                if file.name == testlog:
                    plog = open(testpastlog, 'a+')
                else:
                    plog = open(pastlog, 'a+')
                plog.write(tocomp)
                plog.close()
            else:
                print line,
        fil.close()
        response = 'completed "' + match[0] + '"'

    return response

def help(args):
    response = ''

    if args == '':
        response = 'add | remove | comp | edit | attending | missing | list | past | source | help [command]'
    elif not args in cmdlist:
        response = 'command not implemented'
    else:
        if args == 'add':
            response = 'add <trip>: adds the trip to list'
        elif args == 'remove':
            response = 'remove <keys>: removes trip containing <keys> from list.'
        elif args == 'comp':
            response = 'comp <keys>: moves trip containing <keys> from list to past.'
        elif args == 'edit':
            response = 'edit <keys> <s/old/new/>: changes old to new in trip containing <keys>. remember to escape "/" by using "\/" if they occur in old or new.'
        elif args == 'attending':
            response = 'attending <keys>: adds your nick to the attending list for the trip containing <keys>'
        elif args == 'missing':
            response = 'missing <keys>: removes your nick from the attending list for the trip containing <keys>'
        elif args == 'list':
            response = 'list: lists current trip ideas. the listing is sorted by date, with trips missing dates at the end'
        elif args == 'past':
            response = 'past: lists completed trips'
        elif args == 'source':
            response = 'source: gives link to source for trailbot'

    return response

def list():
    tolist = getcontents(file)
    tolist = sorttrips(tolist)

    if len(tolist) > 0:
        first = 'the next trip is "' + tolist[0] + '", sending the full list in a pm'
        tolist.insert(0, first)

    return tolist

def past():
    if file.name == testlog:
        p = open(testpastlog, 'a+')
    else:
        p = open(pastlog, 'a+')
    done = getcontents(p)
    p.close()
    
    done.insert(0, 'sending past trips list in pm')
    return done

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
            file = open(testlog, 'a+')
        else:
            file = open(log, 'a+')

        if cmd == 'attending' or cmd == 'missing':
            args = [user] + [args]

        if cmd not in cmdlist:
            reply = 'command not implemented'            
        elif cmd in cmdlist[:magicnumber]:
            reply = globals()[cmd](args)
        elif cmd in cmdlist[magicnumber:]:
            reply = globals()[cmd]()

        file.close()
    elif msg.startswith('trailbot'):
        reply.append('prefix commands with "@"')
    else:
        reply = ''

    return reply

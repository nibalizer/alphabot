#!/usr/bin/env python

import os
import re
import fileinput as fi
from dateutil import parser

MAGIC_NUMBER = 7

cmdlist = ['add', 'remove', 'edit', 'comp', 'help', 'attending', 'missing',
           'list', 'past', 'source']
log = './trip.log'
past_log = './past.log'
test_log = './test.log'
testpast_log = './testpast.log'
file = None

def get_contents(f):
    if f.tell():
        f.seek(0, 0)

    lines = f.readlines()
    lines = [l[:-1] for l in lines]
    return lines

def sort_trips(list):
    dated = []
    undated = []
    sort_dict = {}

    for e in list:
        if re.search(r'(^|\s)[0-9][0-9]?/[0-9][0-9]?($|\s|,|\.|\?|!)', e):
            dated.append(e)
        else:
            undated.append(e)

    dates = [parser.parse(x, fuzzy=True) for x in dated]
    for x in range(len(dates)):
        sort_dict[dates[x]] = dated[x]

    dates.sort(key = lambda x: x.timetuple()[1:3])
    dated = [sort_dict[x] for x in dates]

    return dated + undated

def add(args):
    if not args:
        return ''

    file.write(args + '\n')
    return 'added "' + args + '"'

def remove(args):
    response = ''
    trips = get_contents(file)

    if not args:
        return response

    match = filter(lambda e: args in e, trips)
    if not len(match):
        response = 'no matching trips found'
    else:
        to_del = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line != to_del: 
                print line,
        response = 'removed "' + match[0] + '"'
        fil.close()
    return response

def edit(args):
    response = ''
    trips = get_contents(file)
    cmd_index = 0

    if not args:
        return response

    args = args.rsplit()
    for e in args:
        if 's/' in e:
            cmd_index = args.index(e)
            break
    search = ' '.join(args[:cmd_index])
    command = ' '.join(args[cmd_index:])

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
        if not len(match):
            response = 'no matching trips found'
        else:
            to_edit = match[0] + '\n'
            edited = ''
            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == to_edit:
                    edited = line.replace(old, new, 1)
                    print edited,
                else:
                    print line,
            fil.close()
            response = 'changed "' + match[0] + '" to "' + edited[:-1] + '"'
                
    return response    


def attending(args):
    response = ''
    trips = get_contents(file)
    if len(args) > 1:
        user = args[0]
        args = args[1]

    if not args:
        return response

    match = filter(lambda e: args in e, trips)
    if not len(match):
        response = 'no matching trips found'
    else:
        has_att = True
        att_index = 0
        match = match[0].rsplit()
        for e in match:
            if '|attending|' in e:
                att_index = match.index(e)

        if not att_index:
            has_att = False

        if has_att and user in match[att_index:]:
            response = 'appreciate the enthusiasm, but you '\
                                 'already said you would go'
        else:
            match = ' '.join(match)
            to_attend = match + '\n'
            attending = ''
            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == to_attend:
                    if has_att:
                        attending = line[:-1] + ' ' + user + '\n'
                        print attending,
                    else:
                        attending = line[:-1] + ' |attending| ' + user \
                                                                + '\n'
                        print attending,
                else:
                    print line,
            fil.close()
            response = user + ' is now attending "' + attending[:-1] + '"' 
                    
    return response

def missing(args):
    response = ''
    trips = get_contents(file)
    if len(args) > 1:
        user = args[0]
        args = args[1]

    if not args:
        return response

    match = filter(lambda e: args in e, trips)
    if not len(match):
        response = 'no matching trips found'
    else:
        has_att = True
        att_index = 0
        match = match[0].rsplit()
        for e in match:
            if '|attending|' in e:
                att_index = match.index(e)

        if not att_index:
            has_att = False

        if not has_att:
            response = "no one is going yet" 
        elif user not in match[att_index:]:
            response = "you aren't attending yet" 
        else:
            match = ' '.join(match)
            to_miss = match + '\n'
            missing = ''
            fil = fi.FileInput(file.name, inplace=1)
            for line in fil:
                if line == to_miss:
                    start = line.rsplit('|attending|')[0]
                    finish = line.rsplit('|attending|')[1].rsplit()

                    if len(finish) == 1:
                        missing = start[:-1] + '\n'
                        print missing,
                    else:
                        finish.remove(user)
                        missing = start + '|attending| ' + ' '.join(finish) \
                                                                     + '\n'
                        print missing,
                else:
                    print line,
            fil.close()
            response = user + ' is now missing "' + missing[:-1] + '"' 

    return response

def comp(args):
    response = ''
    trips = get_contents(file)

    if not args:
        return response

    match = filter(lambda e: args in e, trips)
    if not len(match):
        response = 'no matching trips found'
    else:
        to_comp = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line == to_comp:
                if file.name == test_log:
                    plog = open(testpast_log, 'a+')
                else:
                    plog = open(past_log, 'a+')
                plog.write(to_comp)
                plog.close()
            else:
                print line,
        fil.close()
        response = 'completed "' + match[0] + '"'

    return response

def help(args):
    response = ''

    if not args:
        response = 'add | remove | comp | edit | attending | missing | list ' \
                                           '| past | source | help [command]'
    elif not args in cmdlist:
        response = 'command not implemented'
    else:
        if args == 'add':
            response = 'add <trip>: adds the trip to list'
        elif args == 'remove':
            response = 'remove <keys>: removes trip containing <keys> from ' \
                                                                     'list.'
        elif args == 'comp':
            response = 'comp <keys>: moves trip containing <keys> from list ' \
                                                                   'to past.'
        elif args == 'edit':
            response = 'edit <keys> <s/old/new/>: changes old to new in ' \
                       'trip containing <keys>. remember to escape "/" by ' \
                                  'using "\/" if they occur in old or new.'
        elif args == 'attending':
            response = 'attending <keys>: adds your nick to the attending ' \
                                      'list for the trip containing <keys>'
        elif args == 'missing':
            response = 'missing <keys>: removes your nick from the attending ' \
                                         'list for the trip containing <keys>'
        elif args == 'list':
            response = 'list: lists current trip ideas. the listing is sorted ' \
                                 'by date, with trips missing dates at the end'
        elif args == 'past':
            response = 'past: lists completed trips'
        elif args == 'source':
            response = 'source: gives link to source for trailbot'

    return response

def list():
    to_list = get_contents(file)
    to_list = sort_trips(to_list)

    if len(to_list):
        first = 'the next trip is "' + to_list[0] + '", sending the full list ' \
                                                                      'in a pm'
        to_list.insert(0, first)

    return to_list

def past():
    if file.name == test_log:
        p = open(testpast_log, 'r')
    else:
        p = open(past_log, 'r')
    done = get_contents(p)
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
            file = open(test_log, 'a+')
        else:
            file = open(log, 'a+')
        if cmd == 'attending' or cmd == 'missing':
            args = [user] + [args]

        if cmd not in cmdlist:
            reply = 'command not implemented'            
        elif cmd in cmdlist[:MAGIC_NUMBER]:
            reply = globals()[cmd](args)
        elif cmd in cmdlist[MAGIC_NUMBER:]:
            reply = globals()[cmd]()
        file.close()
    elif msg.startswith('trailbot'):
        reply.append('prefix commands with "@"')
    else:
        reply = ''

    print reply
    return reply

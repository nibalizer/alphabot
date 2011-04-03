#!/usr/bin/env python

"""The meat and bones of trailbot functionality, a collection of methods.

This is where most of the work was put in on trailbot to process all the
commands and return appropriate replies. The module is used through the
dispatch method that calls the proper command method and opens the proper
files to interact with.

There are a few utility methods for repetitive code, probably more to come
when I get around to cleaning things up, but for the most part each method
is a trailbot command.

The replies from trailbot are snarky, for sure, and I hope to add more fun
bits to keep things interesting.

"""

import os
import re
import fileinput as fi
import docs

from dateutil import parser

# magic number for global() call in dispatch slicing
MAGIC_NUMBER = 5

# list of commands currently supported by trailbot
cmdlist = ['add', 'remove', 'edit', 'comp', 'help', 'list', 'past', 'source']

# files associated with logging trips
log = './trip.log'
past_log = './past.log'
test_log = './test.log'
testpast_log = './testpast.log'

# global file descriptor for working with the open log
file = None

def get_contents(f):
    """pulls lines from the open file, trims '\n',and returns list of lines"""

    if f.tell():
        f.seek(0, 0)

    lines = f.readlines()
    lines = [l[:-1] for l in lines]
    return lines

def sort_trips(list):
    """sorts a list of trips by date, appending trips without dates

    This method takes in a list of trips that may or may not contain dates.
    It breaks the list into to lists, one containing dated trips and the other
    containing undated trips, using a regex to test each line.

    dateutil's fuzzy parser is then used to return a list of corresponding
    datetime objects from the dated list. The dated list and datetime list is
    zipped into a dictionary and sorted by the datetime object keys.

    Finally, the now sorted dated trip values are returned with the undated
    trips appended to the end of them.

    """

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
    """adds trip and google doc to log
    
    This checks for something to add, gets a link from a new google doc made
    in docs.docify(), and appends the info to the trip. It then writes the
    trip out to the log and returns a success reply.

    """

    if not args:
        return ''

    link = docs.docify(args)
    args = args + ' | rsvp/share cars here: ' + link

    file.write(args + '\n')
    return 'added "' + args + '"'

def remove(args):
    """removes a trip and it's doc that matches the args from the log
    
    This method searches for a case insensitive matching trip in the log based
    on keywords found in args. If a match is made, the google doc for that trip
    is trashed and the trip entry in the log is deleted. The method returns a 
    confirmation with the trip removed. 
    
    """

    response = ''
    trips = get_contents(file)

    if not args:
        return response
    
    match = filter(lambda e: re.search(args, e, re.I), trips)
    if not len(match):
        response = "couldn't find one for you with that info"
    else:
        docs.dedocify(args)
        to_del = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line != to_del: 
                print line,
        response = 'i got rid of "' + match[0] + '"'
        fil.close()
    return response

def edit(args):
    """edits a trip entry, using s/<old>/<new>/
    
    This takes a string of any number of keywords followed by the sequence 
    's/<old>/<new>/'. It finds the trip matching the keyword(s) and replaces
    <old> with <new>, which can both be any number of words/characters.

    Note that <old> and <new> args containing '/' need to be escaped as '\/'
    to parse correctly.

    The method splits up the string to keywords and 's/<old>/<new>/', checks
    the format of 's/<old>/<new>/', replaces '\/' with '/' if they're used,
    then starts to search for the matching trip.

    Once a trip entry matching the keyword(s) is found, <old> is replaced with
    <new> and the new trip is returned as a confirmation response.

    """

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
        response = "you are doing it wrong. it's '@edit <keys> s/<old>/<new>/"
    else:
        # separates <old> and <new> and deals with \/ if it's there
        old = re.split(r'(?<!\\)/', command)[1]
        new = re.split(r'(?<!\\)/', command)[2]
        if '\/' in old:
            old = old.replace('\/', '/')
        if '\/' in new:
            new = new.replace('\/', '/')

        match = filter(lambda e: re.search(search, e, re.I), trips)
        if not len(match):
            response = "couldn't find one for you with that info"
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
            response = 'i changed that thing and now i\'ve got the trip as "' + \
                                                             edited[:-1] + '"'
                
    return response    

def comp(args):
    """completes a trip by moving it to the past log
    
    This completes a recent trip by finding the entry in the log and moving it
    to the past log for viewing with past(). It includes logic when editing the
    files to move the trip to the test log or actual log depending on the 
    command issued.

    A confirmation message with the trip is returned when successful.

    """

    response = ''
    trips = get_contents(file)

    if not args:
        return response

    match = filter(lambda e: re.search(args, e, re.I), trips)
    if not len(match):
        response = "couldn't find one for you with that info"
    else:
        docs.dedocify(args)
        to_comp = match[0] + '\n'
        fil = fi.FileInput(file.name, inplace=1)
        for line in fil:
            if line == to_comp:
                if file.name == test_log:
                    plog = open(testpast_log, 'a+')
                else:
                    plog = open(past_log, 'a+')

                # removes the google doc info before writing to the past log
                to_comp = to_comp[:to_comp.index(' | rsvp/share')] + '\n'
                plog.write(to_comp)
                plog.close()
            else:
                print line,
        fil.close()
        response = '"' + to_comp[:-1] + '" was fun, is done, and can be seen ' \
                                                             'in the past log'
    return response

def help(args):
    """displays all help information available

    This is the main help method for commands available in trailbot. With no
    arguments, it returns a list of commands. If a specific command is given
    as an argument, it will return a more detailed explanation of the command
    and parameters that it requires.

    """

    response = ''

    if not args:
        response = 'add | remove | comp | edit | list | past | source | help ' \
                                                                   '[command]'
    elif not args in cmdlist:
        response = "either i don't know that one, or i don't want to know " \
                                                                 "that one"
    else:
        if args == 'add':
            response = "add <trip>: adds the trip to the list and appends a " \
                       "link to a handy dandy google doc with ride, meeting " \
                                                    "location, and rsvp info"
        elif args == 'remove':
            response = "remove <keys>: deletes the trip from the list that " \
                       "matches whatever keyword(s) you give, and don't " \
                                                       "worry about case"
        elif args == 'comp':
            response = "comp <keys>: completes a trip and moves it to the " \
                                               "past log for fond memories"
        elif args == 'edit':
            response = "edit <keys> s/<old>/<new>/: replaces the old with " \
                       "the new in the trip matching whatever keyword(s). " \
                       "old and new can be any number of words/characters, " \
                       "just escape '/' with '\/' if you're editing that."
        elif args == 'list':
            response = "list: shows the next trip that has a date in the " \
                       "channel, then sends the full list of trip to you in " \
                       "private message (because who likes spam?)"
        elif args == 'past':
            response = "past: sends a private message with all the past " \
                       "trips that've been done for nostalgia's sake"
        elif args == 'source':
            response = "source: gives the github link for my bits and pieces"

    return response

def list():
    """lists the current trips in the log

    This pulls all the trips from the current log file, sorts them with
    sort_trips() by date, then returns a list of the trips.

    """

    to_list = get_contents(file)
    to_list = sort_trips(to_list)

    if len(to_list):
        first = "next up is " + to_list[0] + " and i'm sending the full " \
                                                "list in a private message"
        to_list.insert(0, first)

    return to_list

def past():
    """shows the past trips written to the past log

    This opens the real or test past log, depending on the command issue, 
    and returns the list of past trips from that log.

    """
    
    if file.name == test_log:
        p = open(testpast_log, 'r')
    else:
        p = open(past_log, 'r')
    done = get_contents(p)
    p.close()

    done.insert(0, "prepare for nostalgia via private message")
    return done

def source():
    """returns a link to the trailbot repo on github"""

    return 'you can find all my lovely bits and pieces at ' \
           'https://github.com/dzhurley/trailbot | join #trailbot if you feel' \
           ' like screwing around with me *wink* *wink*'

def dispatch(user, channel, msg):
    """opens the proper log file and calls the proper command method in the msg
    
    This is called from client.py on a privmsg to process commands and work with
    files. If trailbot is addressed directly, a response is returned to check
    out trailbot's help.

    All trailbot commands can be tested by calling '@test cmd [args]' instead of
    '@cmd [args], and doing so utilizes different logs to try stuff out on. That
    way, you don't screw with trips that people may want to actually go on.

    The proper command method is then dispatched with a globals() call and 
    slicing the cmd_list with MAGIC_NUMBER. MAGIC_NUMBER, when slicing the list
    of commands up, gives the commands that take arguments on the left and the
    commands with no arguments on the right.
    
    This reduces many possible elif statements down to a few lines, which is 
    pretty cool.'
    
    """

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

        if cmd not in cmdlist:
            reply = "either i don't know that one, or i don't want to know " \
                                                                 "that one"
        elif cmd in cmdlist[:MAGIC_NUMBER]:
            reply = globals()[cmd](args)
        elif cmd in cmdlist[MAGIC_NUMBER:]:
            reply = globals()[cmd]()
        file.close()
    elif msg.startswith('trailbot'):
        reply = "you must be new, you should try '@help'"
    else:
        reply = ''

    return reply

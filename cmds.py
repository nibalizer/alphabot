#!/usr/bin/env python

"""The meat and bones of trailbot functionality, a collection of functions.

This is where most of the work was put in on trailbot to process all the
commands and return appropriate replies. The module is used through the
dispatch function that calls the proper command function and opens the proper
files to interact with.

There are a few utility functions for repetitive code, probably more to come
when I get around to cleaning things up, but for the most part each function
is a trailbot command.

The replies from trailbot are snarky, for sure, and I hope to add more fun
bits to keep things interesting.

"""

import os
import re
import fileinput as fi
import docs
import voice
import random
import tinyurl

from dateutil import parser

# list of commands currently supported by trailbot
cmdlist = ['add', 'remove', 'edit', 'comp', 'photos', 'help',
           'next', 'list', 'past', 'source']

# files associated with logging trips
log = './trip.log'
past_log = './past.log'
test_log = './test.log'
testpast_log = './testpast.log'

# global file descriptor for working with the open log
file = None

def get_contents(f):
    """returns content of file f in list of lines

    This function takes in the open log file and reads its content into a list.
    The list is then stripped of the newline characters and sorted, then
    returned to the calling function.
    
    """

    if f.tell():
        f.seek(0, 0)
    lines = f.readlines()
    lines = [l[:-1] for l in lines]

    return lines

def sort_trips(list):
    """sorts a list of trips by date, appending trips without dates

    This function takes in a list of trips that may or may not contain dates.
    It breaks the list into a dictionary of dated trips (keys are the first 
    date matching in the trip, values are the trips themselves) and a list of
    undated trips.
    
    A new dictionary parsed_dates is then created that is basically the dated
    dictionary with the keys as datetime objects. Those keys are then sorted,
    and the corresponding trip values hold on for the ride.

    Finally, the now sorted dated trip values are returned with the undated
    trips appended to the end of them.

    """

    pre_dated = {}
    pre_undated = []
    parsed_dates = {}

    for e in list:
        match = re.search(r'(^|\s)[0-9][0-9]?/[0-9][0-9]?($|\s|,|\.|\?|!)', e)
        if match:
            pre_dated[match.group()] = e
        else:
            pre_undated.append(e)
    
    for v in pre_dated.keys():
        parsed_date = parser.parse(v, fuzzy=True)
        parsed_dates[parsed_date] = pre_dated[v]

    date_keys = parsed_dates.keys()
    date_keys.sort(key = lambda x: x.timetuple()[1:3])
    dated = [parsed_dates[x] for x in date_keys]

    return dated + pre_undated

def add(*args):
    """adds trip and google doc to log
    
    This checks for something to add, gets a link from a new google doc made
    in docs.docify(), and appends the info to the trip. The function then reads
    in the current file and inserts the new trip in sorted order, then writes
    the file back out in order. A confirmation response is returned.

    """

    if args and not args[0]:
        return ''
    else:
        args = args[0]

    link = docs.docify(args)
    args = args + ' | rsvp/share cars here: ' + link

    lines = get_contents(file) + [args]
    lines = sort_trips(lines)
    lines = [l + '\n' for l in lines]

    if file.tell():
        file.seek(0, 0)
    file.writelines(lines)

    return '"' + args + '" is now in the logs for viewing pleasure.'

def remove(*args):
    """removes a trip and it's doc that matches the args from the log
    
    This function searches for a case insensitive matching trip in the log based
    on keywords found in args. If a match is made, the google doc for that trip
    is trashed and the trip entry in the log is deleted. The function returns a 
    confirmation with the trip removed. 
    
    """

    response = ''
    trips = get_contents(file)

    if args and not args[0]:
        return response
    else:
        args = args[0]
    
    match = filter(lambda e: re.search(args, e, re.I), trips)
    if not len(match):
        response = random.choice(voice.no_match)
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

def edit(*args):
    """edits a trip entry, using s/<old>/<new>/
    
    This takes a string of any number of keywords followed by the sequence 
    's/<old>/<new>/'. It finds the trip matching the keyword(s) and replaces
    <old> with <new>, which can both be any number of words/characters.

    Note that <old> and <new> args containing '/' need to be escaped as '\/'
    to parse correctly.

    The function splits up the string to keywords and 's/<old>/<new>/', checks
    the format of 's/<old>/<new>/', replaces '\/' with '/' if they're used,
    then starts to search for the matching trip.

    Once a trip entry matching the keyword(s) is found, <old> is replaced with
    <new> and the new trip is returned as a confirmation response.
    
    The google doc entry will also be updated to match the edit. At some point.

    """

    response = ''
    trips = get_contents(file)
    cmd_index = 0

    if args and not args[0]:
        return response
    else:
        args = args[0]

    args = args.rsplit()
    for e in args:
        if 's/' in e:
            cmd_index = args.index(e)
            break
    search = ' '.join(args[:cmd_index])
    command = ' '.join(args[cmd_index:])

    form = re.search(r'^s/.*/.*/$', command)
    if not form:
        response = "you are doing it wrong. it's '@edit <keys> s/<old>/<new>/'"
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
            response = random.choice(voice.no_match)
        elif old not in match[0]:
            response = random.choice(voice.no_match)
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

def comp(*args):
    """completes a trip by moving it to the past log
    
    This completes a recent trip by finding the entry in the log and moving it
    to the past log for viewing with past(). It includes logic when editing the
    files to move the trip to the test log or actual log depending on the 
    command issued.

    A confirmation message with the trip is returned when successful.

    """

    response = ''
    trips = get_contents(file)

    if args and not args[0]:
        return response
    else:
        args = args[0]

    match = filter(lambda e: re.search(args, e, re.I), trips)
    if not len(match):
        response = random.choice(voice.no_match)
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

def photos(*args):
    """add a link to photos from a trip on the end of a past trip

    This function is similar to edit in how it handles the syntax. The arguments
    should be a number of keywords for finding a matching past trip followed by
    a link to whatever photos people have. The args are split, then the link is
    checked if it is indeed a link.
    
    Once the syntax is checked, a matching trip for the keywords is found or a 
    "no match" response is given to the channel. If a match is found, the line
    in the file is appended with the link and a confirmation is returned.

    """
        
    response = ''
    cmd_index = 0

    if file.name == test_log:
        p = open(testpast_log, 'r+')
    else:
        p = open(past_log, 'r+')
    trips = get_contents(p)

    if args and not args[0]:
        return response
    else:
        args = args[0]

    args = args.rsplit()
    for e in args:
        if 'http' in e:
            cmd_index = args.index(e)
            break

    keys = ' '.join(args[:cmd_index])
    link = ' '.join(args[cmd_index:])

    form = re.search(r'http', link)
    if not form:
        response = "you are doing it wrong. it's '@photos <keys> <link>'"
    else:
        match = filter(lambda e: re.search(keys, e, re.I), trips)
        if not len(match):
            response = random.choice(voice.no_match)
        else:
            to_photo = match[0] + '\n'
            link = tinyurl.create_one(link)

            fil = fi.FileInput(p.name, inplace=1)
            for line in fil:
                if line == to_photo:
                    if 'awesome photos' in line:
                        print line[:-1] + ', ' + link + '\n',
                    else:
                        print line[:-1] + " | awesome photos can be found " \
                                                     "here: " + link + '\n',
                else:
                    print line,
            fil.close()
            p.close()
            response = 'that past trip "' + to_photo[:-1] + '" now has a nice ' \
                            'little link to the photos you added from the trip.' 
    return response

def help(*args):
    """displays all help information available

    This is the main help function for commands available in trailbot. With no
    arguments, it returns a list of commands. If a specific command is given
    as an argument, it will return a more detailed explanation of the command
    and parameters that it requires.

    """

    response = ''

    if not args:
        return response
    else:
        args = args[0]

    if args and args not in cmdlist:
        response = random.choice(voice.bad_cmd)
    else:
        response = voice.help[args]
    return response

def next(*args):
    """replies with the next planned trip to the channel

    This gets the list of trips from the current log file and returns the first
    trip in the sorted list to the channel, which is effectively the next one.

    """
    response = ''
    to_list = get_contents(file)
    
    if to_list:
        response = to_list[0]
    else:
        response = "i got nothing, you people need to get plannin'"

    return response

def list(*args):
    """lists the current trips in the log

    This pulls all the trips from the current log file and returns a list of
    the trips to the user. A reply to the channel is put in the first element
    of the list, which indicates that the full trip listing is being sent in
    a private message.

    """

    to_list = get_contents(file)

    if to_list:
        first = "check your private messages for a complete listing of trips " \
                                                 "that may or may not happen."
        to_list.insert(0, first)
        return to_list
    else:
        return "you people need to get some trips together, because i've got " \
                                                           "nothing on my end"

def past(*args):
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
    
    if done:
        done.insert(0, "prepare for nostalgia via private message")
        return done
    else:
        return "looks like no one's done anything. sad."

def source(*args):
    """returns a link to the trailbot repo on github"""

    return 'you can find all my lovely bits and pieces at ' \
           'https://github.com/dzhurley/trailbot | join #trailbot if you feel' \
           ' like screwing around with me *wink* *wink*'

def dispatch(user, channel, msg):
    """opens the proper log file and calls the proper command function in the msg
    
    This is called from client.py on a privmsg to process commands and work with
    files. If trailbot is addressed directly, a response is returned to check
    out trailbot's help.

    All trailbot commands can be tested by calling '@test cmd [args]' instead of
    '@cmd [args], and doing so utilizes different logs to try stuff out on. That
    way, you don't screw with trips that people may want to actually go on.

    The proper command function is then dispatched with a globals() call with the
    args given. By implementing each command function with *args, the actual call
    of the function is done in one line, which is pretty awesome.
    
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
            file = open(test_log, 'r+')
        else:
            file = open(log, 'r+')

        if cmd not in cmdlist:
            reply = user + ", " + random.choice(voice.bad_cmd)
        else:
            reply = globals()[cmd](args)
        file.close()
    elif 'trailbot++' in msg:
        reply = user + random.choice(voice.karma_up)
    elif 'trailbot--' in msg:
        reply = user + random.choice(voice.karma_down)
    elif re.match(r'trailbot[ ,:]', msg):
        reply = user + random.choice(voice.addressed)
    else:
        reply = ''

    return reply

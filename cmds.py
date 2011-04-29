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

import re
import fileinput as fi
import voice
import random
import wolfram 

from dateutil import parser

# list of commands currently supported by trailbot
cmdlist = ['add', 'remove', 'edit', 'comp', 'photos', 'help',
           'next', 'show', 'list', 'past', 'source',
           'alpha', 'indef', 'testing', 'fourier']

# files associated with logging trips
log = './trip.log'
past_log = './past.log'
test_log = './test.log'
testpast_log = './testpast.log'

# global file descriptor for working with the open log
open_file = None
def testing(*msg):
    return "seriously?"

def fourier(msg):
    u = wolfram.makequerry('fourier', msg)
    response = u.encode('ascii', 'ignore')
    return response

def alpha(msg):
    u = wolfram.makequerry('raw', msg)
    response = u.encode('ascii', 'ignore')
    return response

def indef(msg):
    u = alpha.makequerry('indef', msg)
    response = u.encode('ascii', 'ignore')
    return response

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



def sort_trips(to_sort):
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

    for e in to_sort:
        match = re.search(r'(^|\s)[0-9][0-9]?/[0-9][0-9]?($|\s|,|\.|\?|!)', e)
        if match:
            pre_dated[match.group()] = e
        else:
            pre_undated.append(e)

    for v in pre_dated.keys():
        parsed_date = parser.parse(v, fuzzy=True)
        parsed_dates[parsed_date] = pre_dated[v]

    date_keys = parsed_dates.keys()
    date_keys.sort(key=lambda x: x.timetuple()[1:3])
    dated = [parsed_dates[x] for x in date_keys]

    return dated + pre_undated


def get_past(f):
    """gets the matching past trips to the open log

    This is a helper function used a few places to return a list of past trips
    that correspond to the open log file. It also returns the name for the
    proper past log for future use.

    """
    name = ''

    if f.name == test_log:
        name = testpast_log
    else:
        name = past_log
    p = open(name, 'r+')
    past_trips = get_contents(p)
    p.close()
    return past_trips, name


def check_syntax(args, index_key, regex):
    """general syntax checker for edit and photos commands

    This takes in the string of arguments, start of the second argument, and
    the form the second argument should be in. The args string is split on the
    index of the index_key into the first and second arguments, then the form
    of the second argument is checked against a regex for proper form. All of
    these new variables: first, second, and form, are return to the calling
    function.

    """

    cmd_index = 0

    args = args.rsplit()
    for e in args:
        if index_key in e:
            cmd_index = args.index(e)
            break
    first = ' '.join(args[:cmd_index])
    second = ' '.join(args[cmd_index:])
    form = re.search(regex, second)

    return first, second, form


def picket_fence(command):
    """separates old and new and deals with \/ if it's there

    This helps the edit function by splitting the 's/old/new/' string into old
    and new strings, also replacing '\/' with '/' if it exists. Both the old
    and the new are returned.

    """

    old = re.split(r'(?<!\\)/', command)[1]
    new = re.split(r'(?<!\\)/', command)[2]
    if '\/' in old:
        old = old.replace('\/', '/')
    if '\/' in new:
        new = new.replace('\/', '/')

    return old, new










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
    args = args[0]

    if args and args not in cmdlist:
        response = random.choice(voice.bad_cmd)
    else:
        response = voice.help[args]
    return response



def show(*args):
    """displays a matching trip to the channel from any log

    A simple enough function to return a matching trip to the channel. I
    figure someone will use it. It takes in keywords as arguments, does a
    case insensitive search, then returns a match if found, other it returns
    a no_match response from voice.py.

    The current log will first be searched, and if a match isn't found the
    corresponding past log will be searched. This should add a nice touch to
    the channel, being able to share the past trips and possibly photos.

    """

    response = ''
    trips = get_contents(open_file)

    if args and not args[0]:
        return random.choice(voice.missing_arg)
    args = args[0]

    match = filter(lambda e: re.search(args, e, re.I), trips)
    if not len(match):
        past_trips, past_name = get_past(open_file)
        past_match = filter(lambda e: re.search(args, e, re.I), past_trips)
        if not len(past_match):
            response = random.choice(voice.no_match)
        else:
            response = 'i found "' + past_match[0] + '" for you'
    else:
        response = 'i found "' + match[0] + '" for you'
    return response


def list(*args):
    """lists the current trips in the log

    This pulls all the trips from the current log file and returns a list of
    the trips to the user. A reply to the channel is put in the first element
    of the list, which indicates that the full trip listing is being sent in
    a private message.

    """

    to_list = get_contents(open_file)

    if to_list:
        first = "check your private messages for a complete listing of the " \
            "trips that may or may not happen."
        to_list.insert(0, first)
        return to_list
    else:
        return "you people need to get some trips together, 'cause i've got " \
                                                           "nothing on my end"


def past(*args):
    """shows the past trips written to the past log

    This opens the real or test past log, depending on the command issue,
    and returns the list of past trips from that log.

    """

    past_trips, past_name = get_past(open_file)
    if past_trips:
        past_trips.insert(0, "prepare for nostalgia via private message")
        return past_trips
    else:
        return "looks like no one's done anything. sad."


def source(*args):
    """returns a link to the trailbot repo on github"""

    return 'you can find all my lovely bits and pieces at ' \
           'https://github.com/dzhurley/trailbot | #trailbot if you feel' \
           ' like screwing around with me *wink* *wink*'


def dispatch(user, msg):
    """opens the proper log file and calls the command function in the msg

    This is called from client.py in privmsg to process commands and work with
    files. If trailbot is addressed directly, a response is returned to check
    out trailbot's help.

    All trailbot commands can be tested by using '@test cmd [args]' instead of
    '@cmd [args], and doing so utilizes different logs to try stuff on. That
    way, you don't screw with trips that people may want to actually go on.

    The command function is then dispatched with a globals() call with the
    args given. By implementing each command function with *args, the actual
    dispatch of the function is done in one line, which is pretty awesome.

    """

    reply = None
    global open_file

    if msg[0] == '%':
        msg = msg[1:]
        cmd = msg.rsplit()[0]
        args = ' '.join(msg.rsplit()[1:])

        if cmd == 'test':
            cmd = msg.rsplit()[1]
            args = ' '.join(msg.rsplit()[2:])
            open_file = open(test_log, 'r+')
        else:
            open_file = open(log, 'r+')

        if cmd not in cmdlist:
            reply = user + ", " + random.choice(voice.bad_cmd)
        else:
            reply = globals()[cmd](args)
        open_file.close()
    elif 'trailbot++' in msg:
        reply = user + random.choice(voice.karma_up)
    elif 'trailbot--' in msg:
        reply = user + random.choice(voice.karma_down)
    elif re.match(r'trailbot[ ,:]', msg):
        reply = user + random.choice(voice.addressed)
    else:
        reply = ''

    return reply

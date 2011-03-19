#!/usr/bin/env python

def dispatch(user, channel, msg):
    line = ''

    if msg[0] == '@':
        msg = msg[1:]
        line = user.split("!",1)[0] + ' said ' + '"' + msg + '"' + ' in ' + channel
    else:
        line = 'prefix commands with "@"'

    return line

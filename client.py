#!/usr/bin/env python

"""Client module that contains all the twisted bits to keep trailbot alive.

This module contains the TrailBot class for IRC actions, TrailBotFactory to
set up the trailbot protocol, and TrailBotContextFactory for ssl support.
"""

from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

import types
import cmds
import voice
import random

class TrailBot(irc.IRCClient):
    """Main bot interface with IRC happenings

    This class hooks into various IRC actions and handles them appropriately.

    """

    def __init__(self):
        self.nicks = []

    @property
    def _get_nickname(self):
        return self.factory.nickname

    nickname = _get_nickname

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in self.factory.channels:
            self.join(chan)

    def joined(self, channel):
        """on channel join, trailbot gets everyone's nicks"""
        self.sendLine('NAMES')
        self.msg(channel, random.choice(voice.joined))

    def irc_RPL_NAMREPLY(self, prefix, params):
        """unions NAMES and nicks from nicks.log to avoid greeting flappers

        This method is called whenever a reply to NAMES is sent back from the
        IRC server. It puts those names in a list, stripping the voices/ops
        characters, then unions that list with a list of saved nicks. This
        new list is then stored so whenever people join that have already been
        in the channel, trailbot doesn't greet them again.

        """

        from_split = params[3].split()
        for e in from_split:
            if e[0] in '+@':
                e = e[1:]
            self.nicks.append(e)

        nick_file = open('./nicks.log', 'r+')
        from_file = nick_file.readlines()
        from_file = [l[:-1] for l in from_file]

        self.nicks = list(set(self.nicks) | set(from_file))

        to_write = [e + '\n' for e in self.nicks]
        nick_file.seek(0, 0)
        nick_file.writelines(to_write)
        nick_file.close()

    def irc_NICK(self, prefix, params):
        """adds the new nick to the list of nicks not to greet"""
        if params:
            self.nicks.append(params[0])

            nick_file = open('./nicks.log', 'a+')
            nick_file.write(params[0] + '\n')
            nick_file.close()

    def userKicked(self, kickee, channel, kicker, message):
        self.msg(channel, kicker + random.choice(voice.saw_kick))

    def userJoined(self, user, channel):
        """greets a new user to the channel"""
        if user not in self.nicks:
            self.msg(channel, user + random.choice(voice.user_joined[channel]))
            self.nicks.append(user)
            nick_file = open('./nicks.log', 'a+')
            nick_file.write(user + '\n')
            nick_file.close()

    def userLeft(self, user, channel):
        self.msg(channel, random.choice(voice.user_left))

    def privmsg(self, user, channel, msg):
        """Handles user messages from channels

        This hooks every privmsg sent to the channel and sends the commands off
        to cmds.dispatch to process, then replies to the channel accordingly.

        The @reload command needs to be handled here though, as it allows edits
        to be made to trailbot without disconnecting from IRC. It should get a
        list from cmds.dispatch if it needs to pm someone, otherwise it gets a
        string back and msgs the channel.

        """
        user = user.split('!', 1)[0]

        if msg == '%reload':
            rebuild.rebuild(cmds)
            rebuild.rebuild(voice)
            self.msg(channel, 'reloaded and ready to go')
        else:
            reply = cmds.dispatch(user, msg)

            if type(reply) is types.StringType:
                self.msg(channel, reply)
            else:
                if len(reply):
                    self.msg(channel, reply[0])
                    for trip in reply[1:]:
                        self.msg(user, trip)

    def modeChanged(self, user, channel, set, modes, args):
        """responds is trailbot is given a mode"""
        if set and user == self.nickname:
            random.choice(voice.mode_set)


class TrailBotFactory(protocol.ClientFactory):
    """Subclass of ClientFactory for trailbot protocol"""

    protocol = TrailBot

    def __init__(self, channels, nickname):
        self.channels = channels
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        print 'connection lost',
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed',


class TrailBotContextFactory(ssl.ClientContextFactory):
    """Subclass of ClientContextFactory for ssl connection"""

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        return ctx

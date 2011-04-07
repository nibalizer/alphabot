#!/usr/bin/env python

"""Client module that contains all the twisted bits to keep trailbot alive.

This module contains the TrailBot class for IRC actions, TrailBotFactory to
set up the trailbot protocol, and TrailBotContextFactory for ssl support.
"""

from OpenSSL import SSL
from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

import types
import cmds
import docs
import voice
import random

class TrailBot(irc.IRCClient):
    """Main bot interface with IRC happenings

    This class hooks into various IRC actions and handles them appropriately.

    """

    def _get_nickname(self):
        return self.factory.nickname
    # stores trailbot's nick in TrailBot
    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        # once connected, trailbot joins the channels set up in TrailBotFactory
        for chan in self.factory.channels:
            self.join(chan)

    def joined(self, channel):
        self.msg(channel, random.choice(voice.joined))

    def userKicked(self, kickee, channel, kicker, message):
        self.msg(channel, kicker + random.choice(voice.saw_kick))
    
    def userJoined(self, user, channel):
        """greetings for user joining each channel"""
        self.msg(channel, user + voice.user_joined[channel])

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
        user = user.split('!',1)[0]
        
        if msg == '@reload':
            rebuild.rebuild(cmds)
            rebuild.rebuild(docs)
            rebuild.rebuild(voice)
            self.msg(channel, 'reloaded and ready to go')
        else:
            reply = cmds.dispatch(user, channel, msg)

            if type(reply) is types.StringType:
                self.msg(channel, reply) 
            else:
                if len(reply):
                    self.msg(channel, reply[0])
                    for trip in reply[1:]:
                        self.msg(user, trip)                

class TrailBotFactory(protocol.ClientFactory):
    """Subclass of ClientFactory for trailbot protocol"""

    protocol = TrailBot

    def __init__(self, channels, nickname):
        self.channels = channels
        self.nickname = nickname

    def clientConnectionLost(self, connector, reason):
        # if the connection is lost, try to reconnect
        print 'connection lost',
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        # give up
        print 'connection failed',

class TrailBotContextFactory(ssl.ClientContextFactory):
    """Subclass of ClientContextFactory for ssl connection"""

    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        return ctx

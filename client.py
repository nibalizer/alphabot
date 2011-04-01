#!/usr/bin/env python

from OpenSSL import SSL
from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

import types
import cmds
import docs

class TrailBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        for chan in self.factory.channels:
            self.join(chan)

    def userKicked(self, kickee, channel, kicker, message):
        self.msg(channel, 'damn...')

    def privmsg(self, user, channel, msg):
        user = user.split('!',1)[0]

        if msg == '@reload':
            rebuild.rebuild(cmds)
            rebuild.rebuild(docs)
            self.msg(channel, 'cmds updated')
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
    def getContext(self):
        ctx = ssl.ClientContextFactory.getContext(self)
        return ctx

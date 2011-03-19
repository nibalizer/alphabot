#!/usr/bin/env python

from OpenSSL import SSL
from twisted.words.protocols import irc
from twisted.internet import protocol, ssl
from twisted.python import rebuild

import cmds

class TrailBot(irc.IRCClient):
    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)

    def signedOn(self):
        self.join(self.factory.channel)

    def privmsg(self, user, channel, msg):
        line = ''

        if msg == '@reload':
            rebuild.rebuild(cmds)
            line = 'cmds updated'
        else:
            line = cmds.dispatch(user, channel, msg)

        irc.IRCClient.msg(self, channel, mesg)

class TrailBotFactory(protocol.ClientFactory):
    protocol = TrailBot

    def __init__(self, channel, nickname):
        self.channel = channel
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

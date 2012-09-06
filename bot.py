#!/usr/bin/env python

"""Bot class and main method.

This module contains the Bot class that is trailbot and the main method to
connect and join irc channels, then stick around for commands.
"""

from twisted.internet import reactor
from client import TrailBotFactory, TrailBotContextFactory


class Bot:
    """Bot instance for trailbot

    This defines the instance and connection parameters for trailbot, and
    also contains a method to connect via ssl and start the  reactor.
    """

    def __init__(self):
        """trailbot info for connecting and joining channels"""
        self.host = 'irc.cat.pdx.edu'
        self.port = 6697
        self.chans = ['#alphabot']
        self.nick = 'alphabot'

    def start(self):
        """connects over ssl to the irc server and starts the reactor"""
        reactor.connectSSL(self.host, self.port,
                           TrailBotFactory(self.chans, self.nick),
                           TrailBotContextFactory())
        reactor.run()


def main():
    """initializes trailbot and starts the connection to irc"""

    trailbot = Bot()
    trailbot.start()

if __name__ == "__main__":
    main()

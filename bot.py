#!/usr/bin/env python
#
# trailbot mk2

from twisted.internet import reactor
from client import TrailBotFactory, TrailBotContextFactory

class Bot:
    def __init__(self):
        self.host = 'irc.cat.pdx.edu'
        self.port = 6697
        self.chan = 'trailbot'
        self.nick = 'trailbot2'
        
    def start(self):
        reactor.connectSSL(self.host, self.port, TrailBotFactory('#'+self.chan,self.nick), TrailBotContextFactory())
        reactor.run()

def main():
    trailbot = Bot()
    trailbot.start()

if __name__ == "__main__":
    main()

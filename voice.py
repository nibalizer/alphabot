#!/usr/bin/env python

"""the voice of trailbot

This module contains all the replies trailbot can send to a channel,
organized into the various contexts that trailbot should say something.

By pulling all the fun replies out of client.py and cmds.py, more responses
can be added and reloaded without disconnecting from IRC. Help is also in
this module to minimize the code in cmds.py.

"""

user_joined = {'#trailbot': ", try and break me, please, just enter in all " \
                  "commands as '@test cmd [args]' and not '@cmd [args]'. that " \
                    "way i'll use a new set of logs and not the ones for #afk.",
               '#afk': "welcome to a channel of wonder and mystery, where " \
                   "people get together and do stuff outside."}

user_left = ["looks like we lost another one, that's a shame."]

joined = ["d-_-b probably screwed something up",
          "well that was a nice break",
          "let's see if i work this time around"]

saw_kick = [", that was a little harsh",
            ", what did they ever do to you?",
            ", you are just a mean person"]

bad_cmd = ["either i don't know that one, or i don't want to know that one",
           "not sure what you're trying to do there, don't know that one",
           "something went wrong, but it was on your end"]

no_match = ["couldn't find one for you with that info",
            "no match, you sure you're looking for the right thing?",
            "i found nothing to work with on my end with that info"]

help = {'': 'add | remove | comp | edit | list | past | source | help ' \
                                                            '[command]',
        'add': "add <trip>: adds the trip to the list and appends a link to " \
            "a handy dandy google doc with ride, meeting place, and rsvp info",
        'remove': "remove <keys>: deletes the trip from the list that matches " \
            "whatever keyword(s) you give, and don't worry about case",
        'comp': "comp <keys>: completes a trip and moves it to the past log " \
            "for fond memories",
        'edit': "edit <keys> s/<old>/<new>/: replaces the old with the new in " \
            "the trip matching whatever keyword(s). old and new can be any " \
            "number of words/characters, just escape '/' with '\/' if you're " \
            "editing that.",
        'list': "list: shows the next trip that has a date in the channel, " \
            "then sends the full list of trip to you in a private message " \
            "(because who likes spam?)",
        'past': "past: sends a private message with all the past trips " \
            "that've been done for nostalgia's sake",
        'source': "source: gives the github link for my bits and pieces"}

addressed = [", you must be new, you should try '@help'",
             ", appreciate the attention, but all my commands start with '@'",
             ", hello to you too, but you won't get anywhere using my nick"]

karma = [", you're too kind, far too kind",
         ", good day sir/madam/genderneutraltitle",
         ", may good luck and better alcohol find their way to you"]

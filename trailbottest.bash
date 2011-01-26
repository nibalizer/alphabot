#!/bin/bash
#
# mangled from bdbot for #afk
#
# testing....................

line=""
fline=""
started=""
remove=""
fromcmds=""
trips="trail.log"
help="add | remove (be specific) | list | help"

socat="socat - openssl:irc.cat.pdx.edu:6697,verify=0"

rm botfile
mkfifo botfile

tail -f botfile | $socat | while true ; do
    if [ -z $started ] ; then
        echo "USER trailbottest 0 trailbottest :immma bot" > botfile
        echo "NICK trailbottest" >> botfile
        echo "JOIN #trailbot" >> botfile
        started="yes"
    fi
    read irc
    case `echo $irc | cut -d " " -f 1` in
        "PING") echo "PONG :`hostname`" >> botfile ;;
    esac

    chan=`echo $irc | cut -d ' ' -f 3`
    barf=`echo $irc | cut -d ' ' -f 1-3`
    cmd=`echo ${irc##$barf :}|cut -d ' ' -f 1|tr -d "\r\n"`
    args=`echo ${irc##$barf :$cmd}|tr -d "\r\n"`
    nick="${irc%%!*}";nick="${nick#:}"

    if [ ! -e "$trips" ] ; then
	echo "PRIVMSG $chan :No log found, making new one" >> botfile
        touch "$trips";
    fi


    if [ "${cmd%[:,]}" == "trailbot" ] ; then
        echo "PRIVMSG $chan :don't talk to me, use '@'" >> botfile
    fi

    case $cmd in
        @*)
            fromcmds="$(./cmds.bash "$cmd" "$args" "$chan")"
            echo "PRIVMSG $chan :$fromcmds" >> botfile
            ;;
    esac
done
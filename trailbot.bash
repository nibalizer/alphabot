#!/bin/bash
#
# mangled from bdbot for #afk
#
# said mangling achieved by d-_-b, aka stutterbug

started=""
trips="trail.log"
help="help.txt"

socat="socat - openssl:irc.cat.pdx.edu:6697,verify=0"

rm botfile
mkfifo botfile

tail -f botfile | $socat | while true ; do
    if [ -z $started ] ; then
        echo "USER trailbot 0 trailbot :trailbot" > botfile
        echo "NICK trailbot" >> botfile
        echo "JOIN #afk" >> botfile
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
        touch "$trips";
    fi


    if [ "${cmd%[:,]}" == "trailbot" ] ; then
        echo "PRIVMSG $chan :don't talk to me, use '@'" >> botfile
    fi

    case $cmd in
        @*)
            fromcmds="$(./cmds.bash "$cmd" "$args")"
            if [ "~" == "${fromcmds:0:1}" ] ; then
                lines=`echo $fromcmds | tr "~" "\n"`
                
                oldifs=$IFS
                IFS=$(echo -en "\n\b")
                
                for line in $lines ; do
                    echo "PRIVMSG $chan :$line" >> botfile
                done
                IFS=$oldifs
            else
                echo "PRIVMSG $chan :$fromcmds" >> botfile
            fi
            ;;
    esac
done
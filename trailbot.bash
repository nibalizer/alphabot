#!/bin/bash
#
# mangled from bdbot for #afk
#

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
    nick="${irc%%!*}"; nick="${nick#:}"

    if [ ! -e "$trips" ] ; then
	echo "PRIVMSG $chan :no log found, creating new log" >> botfile
        touch "$trips";
    fi

    if [ "${cmd%[:,]}" == "trailbot" ] ; then
        echo "PRIVMSG $chan :don't talk to me, use '@'" >> botfile
    fi

    case $cmd in
        "@add")
	        echo "$args" >> $trips
	        echo "PRIVMSG $chan :\"$args\" added" >> botfile
	        ;;
        "@remove")
	        remove=`grep -i "$args" $trips`
	        if [ -z "$remove" ] ; then
		        echo "PRIVMSG $chan :no matching trips" >> botfile
	        else
		        sed -i '' /"$args"/d "$trips"    #remove '' on non-mac
		        echo "PRIVMSG $chan :\"$remove\" removed" >> botfile
	        fi
	        ;;
	    "@list")
	        if [ ! -s "$trips" ] ; then
		        echo "PRIVMSG $chan :no trips found in log" >> botfile
	        fi
	        while read fline
	        do
		        echo "PRIVMSG $chan :$fline" >> botfile 
	        done < "$trips"
	        ;;
	    @*) 
	        if [ ! -s "$help" ] ; then
                echo "PRIVMSG $chan :no help docs found" >> botfile
            fi
            while read fline
            do
                echo "PRIVMSG $chan :$fline" >> botfile
            done < "$help"
            ;;
   esac
done
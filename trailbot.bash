#!/bin/bash
#
# will be adapted to #afk
#

line=""
fline=""
started=""
remove=""
trips="trail.log"
help="all commands start with '@': (add | remove | list | help)"

rm botfile
mkfifo botfile

tail -f botfile | nc irc.cat.pdx.edu 6667 | while true ; do
    if [ -z $started ] ; then
        echo "USER trailbot 0 trailbot :imma bot" > botfile
        echo "NICK trailbot" >> botfile
        echo "JOIN #robots catsonly" >> botfile
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

    case $cmd in
        "@add")
	    line="$args $line"
	    echo "$line" >> $trips
	    echo "PRIVMSG $chan :'$line' added" >> botfile
	    ;;
        "@remove")
	    line="$args $line"
	    remove=`grep "$line" $trips`
	    if [ -z "$remove" ] ; then
		echo "PRIVMSG $chan :No matching trips" >> botfile
	    else
		sed '/$remove/d' "$trips"
		echo "PRIVMSG $chan :'$line' removed" >> botfile
	    fi
	    ;;
	"@list")
	    if [ ! -s "$trips" ] ; then
		echo "PRIVMSG $chan :No trips found in log" >> botfile
	    fi
	    while read fline
	    do
		echo "PRIVMSG $chan :$fline" >> botfile 
	    done < "$trips"
	    ;;
	"@help") 
	    echo "PRIVMSG $chan :$help" >> botfile
	    ;;
   esac
done


#!/bin/bash
#
# should receive args in this order:
# $cmd, $args, $chan
#

trips="trail.log"
help="help.txt"

cmd="$1"
args="$2"
chan="$3"

case $cmd in
    "@add")
	    echo "$args" >> $trips
	    echo "\"$args\" added"
        ;;
    "@remove")
	    remove=`grep -i "$args" $trips`
        if [ -z "$remove" ] ; then
	        echo "no matching trips"
	    else
  	        sed -i '' /"$args"/d "$trips"    #remove '' on non-mac
	        echo "\"$remove\" removed"
	    fi
        ;;
	"@list")
	    if [ ! -s "$trips" ] ; then
		    echo "no trips found in log"
        fi
	    while read fline
	    do
  	        echo "$fline"
	    done < "$trips"
	    ;;
    @*) 
        if [ ! -s "$help" ] ; then
            echo "no help docs found"
        fi
        while read fline
        do
            echo "$fline";
        done < "$help"
        ;;
esac
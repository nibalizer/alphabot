#!/bin/bash
#
# should receive args in this order:
# $cmd, $args
#
# multiline delimiter is '~'


trips="trail.log"
past="past.log"
help="help.txt"

cmd="$1"
args="$2"

multiline_reply () {
    file="$1"

    if [ ! -s "$file" ] ; then
	if [ "$file" == "$help" ] ; then
	    echo "no help found"
	else
            echo "no trips found"
	fi
    else
        multiline=""
        while read fline
        do
            multiline="$multiline~$fline"
	done < "$file"
        echo "$multiline"
    fi
}

case $cmd in
    "@add")
        echo "$args" >> $trips
        echo "\"$args\" added"
        ;;
    "@complete")
	comp=`grep -i "$args" $trips`
        if [ -z "$comp" ] ; then
	        echo "no matching trips"
        else
            sed -i /"$args"/d "$trips"
            echo "\"$comp\" is done"
	    echo "$comp" >> $past
        fi
        ;;
    "@remove")
	remove=`grep -i "$args" $trips`
	rmpast=`grep -i "$args" $past`
        if [ -z "$remove" ] ; then
	    if [ -z "$rmpast" ] ; then
		echo "no matching trips"
	    else
		sed -i /"$args"/d "$past"		
		echo "\"$rmpast\" removed from logs"
	    fi
        else
            sed -i /"$args"/d "$trips"
            echo "\"$remove\" removed from list"
        fi
        ;;
    "@past")
	multiline_reply $past
	;;
    "@list")
	multiline_reply $trips
        ;;
    "@source")
	echo "see https://github.com/stutterbug/trailbot"
	;;
    @*) 
	multiline_reply $help
        ;;
esac


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
	if [ ! -s "$past" ] ; then
	    echo "no past trips found"
	else
	    multiline=""
	    while read fline
	    do
  	        multiline="$multiline~$fline"
	    done < "$past"
            echo "$multiline"
	fi
	;;
    "@list")
        if [ ! -s "$trips" ] ; then
	    echo "no trips found in log"
        fi

        multiline=""
        while read fline
	    do
  	        multiline="$multiline~$fline"
	    done < "$trips"
        echo "$multiline"
	    ;;
    @*) 
        if [ ! -s "$help" ] ; then
            echo "no help docs found"
        fi
        
        multiline=""
        while read fline
        do
            multiline="$multiline~$fline"
        done < "$help"
        echo "$multiline"
        ;;
esac
#!/bin/bash
#
# should receive args in this order:
# $cmd, $args
#
# multiline delimiter is '~'


trips="trail.log"
help="help.txt"

cmd="$1"
args="$2"

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
  	        sed -i /"$args"/d "$trips"
	        echo "\"$remove\" removed"
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
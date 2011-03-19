#!/bin/bash
#
# should receive args in this order:
# $cmd, $args
#
# multiline delimiter is '~'


trips="trail.log"
past="past.log"
help="@add, @comp, @remove, @edit, @past [num|all], @list [num|all], @source, @todo [num|all], @help [command]"
todo="todo.txt"

cmd="$1"
args="$2"
farg=`echo $args | cut -d ' ' -f 1`
rargs=`echo ${args##$farg}`
defaultstop=1

help_helper () {
    if [ -z $farg ] ; then
        echo "$help"
    else
        case $farg in
            "add")
                echo "@add <description> - store in current trips"
                ;;
            "comp")
                echo "@comp <keyword> - move match to past trips"
                ;;
            "remove")
                echo "@remove <keyword> - remove match from all logs"
                ;;
            "edit")
                echo "@edit <keyword> s/<old>/<new>/ - edit <old> to <new> in match"
                ;;
            "past")
                echo "@past [num|all] - list completed trips, default is $defaultstop"
                ;;
            "list")
                echo "@list [num|all] - list planned trips, default is $defaultstop"
                ;;
            "source")
                echo "@source - view link to source"
                ;;
            "todo")
                echo "@todo [num|all] - show current (growing) list of future features, default is $defaultstop"
                ;;
            "help")
                echo "really?"
               ;;
            *)
                echo "command isn't implemented"
                ;;
        esac
    fi
}

multiline_reply () {
    file="$1"
    numlines="$args"
    stop=""

    if [ -z $numlines ] ; then
        stop=$defaultstop
    else
        stop=$numlines
    fi

    if [ ! -s "$file" ] ; then
	    if [ "$file" == "$help" ] ; then
	        echo "no help found"
	    else
            echo "no trips found"
	    fi
    else
        multiline=""
        rlines=0
        while read fline
        do
            multiline="$multiline~$fline"
            let rlines++
            if [ -n $stop -a $stop -eq $rlines >& /dev/null ] ; then
                break
            fi
	    done < "$file"
        echo "$multiline"
    fi
}

case $cmd in
    "@add")
        echo "$args" >> $trips
        echo "\"$args\" added"
#        ./tripsort.pl "$trips"
        ;;
    "@comp")
	    comp=`grep -m 1 -i "$args" $trips`
        if [ -z "$comp" ] ; then
	        echo "no matching trips"
        else
            sed -i /"$comp"/d "$trips"
            echo "$comp" >> $past
            echo "\"$comp\" is done"
	    fi
#        ./tripsort.pl "$past"
        ;;
    "@remove")
	    remove=`grep -m 1 -i "$args" $trips`
	    rmpast=`grep -m 1 -i "$args" $past`
        if [ -z "$remove" ] ; then
	        if [ -z "$rmpast" ] ; then
		        echo "no matching trips"
	        else
		        sed -i /"$rmpast"/d "$past"	
		        echo "\"$rmpast\" removed from logs"
	        fi
        else
            sed -i /"$remove"/d "$trips"
            echo "\"$remove\" removed from list"
        fi
        ;;
    "@edit")
        toedit=`grep -i "$farg" $trips`
        if [ -z "$toedit" ] ; then
	        echo "no matching trips"
        else
            sed -i /"$toedit"/d "$trips"
            toedit=`echo $toedit | sed -e "$rargs"`
            echo "entry is now \"$toedit\""
            echo "$toedit" >> $trips
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
    "@todo")
        multiline_reply $todo
        ;;
    "@help")
        help_helper
        ;;
    @*) 
	    echo "$help"
        ;;
esac
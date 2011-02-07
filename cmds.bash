#!/bin/bash
#
# should receive args in this order:
# $cmd, $args
#
# multiline delimiter is '~'


trips="trail.log"
past="past.log"
temp="temp.log"
help="@add, @comp, @remove, @edit, @past, @list, @sort, @source, @todo, @help [command]"
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
                echo "@past - list completed trips"
                ;;
            "list")
                echo "@list - list planned trips"
                ;;
            "sort")
                echo "@sort - sorts trips by date, with those missing dates at the end"
                ;;
            "source")
                echo "@source - view link to source"
                ;;
            "todo")
                echo "@todo - show current (growing) list of future features"
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

list_sort () {
    while read fline
    do
        linecheck=`echo $fline | grep [0-9]/[0-9]`
        if [ -z "$linecheck" ] ; then
            echo "$fline" >> $temp
        else
            while read line
            do
                insertmonth=`echo $linecheck | grep -Eo [0-9]?[0-9]/ | tr -d '/'`
                insertday=`echo $linecheck | grep -Eo /[0-9]?[0-9] | tr -d '/'`
                linemonth=`echo $line | grep -Eo [0-9]?[0-9]/ | tr -d '/'`
                lineday=`echo $line | grep -Eo /[0-9]?[0-9] | tr -d '/'`

                echo "$insertmonth"

                if [ "$insertmonth" -lt "$linemonth" ] ; then
                    sed /"$line"/i\ "$linecheck" "$temp"
                fi

                if [ "$insertmonth" -eq "$linemonth" ] ; then
                    if [ "$insertday" -le "$lineday" ] ; then
                        sed /"$line"/i\ "$linecheck" "$temp"
                    fi
                fi
            done < "$temp"
        fi
    done < "$trips"
    # mv temp.log trail.log
    # sed -i '' /^$/d $trips
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
        ;;
    "@comp")
	    comp=`grep -m 1 -i "$args" $trips`
        if [ -z "$comp" ] ; then
	        echo "no matching trips"
        else
            sed -i '' /"$args"/d "$trips"
            echo "$comp" >> $past
            echo "\"$comp\" is done"
	    fi
        ;;
    "@remove")
	    remove=`grep -m 1 -i "$args" $trips`
	    rmpast=`grep -m 1 -i "$args" $past`
        if [ -z "$remove" ] ; then
	        if [ -z "$rmpast" ] ; then
		        echo "no matching trips"
	        else
		        sed -i '' /"$rmpast"/d "$past"	
		        echo "\"$rmpast\" removed from logs"
	        fi
        else
            sed -i '' /"$remove"/d "$trips"
            echo "\"$remove\" removed from list"
        fi
        ;;
    "@edit")
        toedit=`grep -i "$farg" $trips`
        if [ -z "$toedit" ] ; then
	        echo "no matching trips"
        else
            sed -i '' /"$toedit"/d "$trips"
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
    "@sort")
        touch "$temp"
        list_sort
        multiline_reply $temp
        rm "$temp"
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
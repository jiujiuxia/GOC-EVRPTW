#!/bin/bash
echo "$#"
if [ "$#" -ne 3 ] ; then
    echo "USAGE: $0 -f server_list_file cmd"
    exit -1
fi
 
file_name=$1
cmd_str=$2
path=$3

serverlist_file="$file_name"
 
if [ ! -e $serverlist_file ] ; then
    echo 'server.list not exist';
    exit 0
fi
 
while read line
do
    #echo $line
    if [ -n "$line" ] ; then
        #echo "DOING--->>>>>" $line "<<<<<<<"
        #echo "ssh $line $cmd_str $path"
        ssh -n $line $cmd_str $path
        if [ $? -ne 0 ] ; then
            echo "error: " $?
        fi
    fi
done < $serverlist_file

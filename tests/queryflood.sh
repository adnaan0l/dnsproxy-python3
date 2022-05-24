#!/bin/bash

function run() {
    for d in $(cat domains_list.txt);
    do
        x=$(( ( RANDOM % 10 )  + 1 ))
        if [ "$x" -le 5 ]; then
            echo "dig @127.0.0.1 $d -p 53"
            dig @127.0.0.1 $d -p 53 &
        else
            echo "dig @127.0.0.1 $d +tcp -p 53"
            dig @127.0.0.1 $d +tcp -p 53 &
        fi
    done
}
run

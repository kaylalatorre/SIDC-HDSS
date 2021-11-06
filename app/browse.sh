#!/bin/bash

if [ $1 ]; then
    for param in $@; do
        case $param in
        
            -p) 
                wslview http://$(hostname -I)/pgadmin4
                break
            ;;

            -c)
                curl http://localhost:8000/$2
                break
            ;;

            *)
                wslview http://localhost:8000/$param
            ;;
        esac
    done
else
    wslview http://localhost:8000/
fi
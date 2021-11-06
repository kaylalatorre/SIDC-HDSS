#!/bin/bash

for param in $@; do
    case $param in
        
        -s) 
            sudo service postgresql start
            sudo service apache2 start
            sudo /etc/init.d/nginx start 
        ;;

	    -r) 
            sudo service postgresql reload
            sudo service apache2 reload
            sudo /etc/init.d/nginx reload
        ;;

	    -t)
            sudo service postgresql stop
            sudo service apache2 stop
            sudo /etc/init.d/nginx stop
        ;;

        -d) 
            uwsgi --ini src_uwsgi.ini
            break 
        ;;

        *)
            echo "option \"$param\" not available"
        ;;
    esac
done
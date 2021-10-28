sudo /etc/init.d/nginx start
wslview http://localhost:8000/
uwsgi --ini src_uwsgi.ini
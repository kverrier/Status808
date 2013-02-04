twistd web --path . --port 8080

python test.py

kill -TERM `cat twistd.pid`

rm twistd*

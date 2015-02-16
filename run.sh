#!/usr/bin/env bash

killall -9 python 2> /dev/null
killall -9 python2 2> /dev/null
killall -9 node 2> /dev/null

(cd classifier; python2 classify_online.py) &
(cd training; node server.js) &

wait
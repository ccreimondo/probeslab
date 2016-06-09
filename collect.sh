#!/bin/sh

SAVE_PATH=$1
TIME_INTERVAL=1    # s

if [ -z "$SAVE_PATH" ]; then
    SAVE_PATH="slabinfo.data"
fi

while [ 1 ]
do
    cat /proc/slabinfo >> $SAVE_PATH
    echo "" >> $SAVE_PATH
    sleep $TIME_INTERVAL
done
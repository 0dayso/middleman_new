#!/usr/bin/env bash

python ./fangtianxia.py &&
python ./maitian.py &&
python ./sohujiaodian.py &&
python ./tuitui99.py &&
python ./woaiwojia.py &&
python ./anjuke.py &&

for file in ./data/*
do
    if test -f $file
    then
        sort $file | uniq > ./result/u_{$file}
    fi
done

python ./update_db.py

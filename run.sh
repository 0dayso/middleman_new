#!/usr/bin/env bash
#/usr/bin/python ./fangtianxia.py &&
#/usr/bin/python ./maitian.py &&
#/usr/bin/python ./sohujiaodian.py &&
#/usr/bin/python ./tuitui99.py &&
#/usr/bin/python ./woaiwojia.py &&
#/usr/bin/python ./anjuke.py &&

for file in `ls data`
do
    if test -f ./data/$file
    then
        echo 'sort ./data/'$file'|uniq > ./result/u_'${file}
        sort ./data/$file | uniq > ./result/u_${file}
        echo 'The line count of u_'$file' is:'
        wc -l ./result/u_${file}
    fi
done

ymd=$(date +%Y%m%d) &&
if [ ! -d ./past/$ymd ]
then
    echo 'mkdir ./past/'$ymd
    mkdir ./past/$ymd
fi

usr/bin/python ./update_db.py &&

echo "mv ./result/* ./past/$ymd" &&
mv ./result/* ./past/$ymd/
#rm -rf ./data/*

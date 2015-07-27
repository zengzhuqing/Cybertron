#!/bin/bash
lists=`find ikb`
for f in $lists;do
    cmd="stat --printf=\"%s\" $f"
    sz=`$cmd`
    echo $sz
    if [ "$sz" == "\"0\"" ]; then
        rm $f
    fi
done

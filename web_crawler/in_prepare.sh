#!/bin/bash
# This prepare is for run selelium in a terminal
function error()
{
    echo "-->error:$*"
    exit 1
}
Xvfb :99 -ac &> /dev/null &
if [ $? -ne 0 ];then
    error "Xvfb start failed"
fi
export DISPLAY=:99

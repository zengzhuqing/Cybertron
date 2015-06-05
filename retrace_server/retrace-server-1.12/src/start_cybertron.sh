#!/bin/bash

nohup python app.py > /dev/null &
nohup python term/crashterm.py > /dev/null &

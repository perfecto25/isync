# ISYNC

INotify-based instant rsync

## Installation

install using virtual env

    python3.6 -m venv venv
    source venv/bin/activate

    (venv) pip install -r requirements

configure systemd startup script

    cp isync.service /etc/systemd/system/
    systemctl daemon-reload

## Configuration

open config.py and modify "paths" variable

include any folder paths you want to monitor for changes (Create, Modify, Delete)

once iSync detects a change, it will rsync the file over to the "remote" server thats defined by "remote" variable

## Start / Stop Isync

    systemctl start isync
    systemctl stop isync

## Logging

you can tail the rsync logs in isync directory 

    cd /opt/isync
    tail -f isync.log
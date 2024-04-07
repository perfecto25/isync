# ISYNC

INotify-based instant rsync

## Installation

install using virtual env

    cd /opt
    
    # git clone this repo
    
    cd /opt/isync
    python3 -m venv venv
    source venv/bin/activate
    (venv) pip install -r requirements.txt

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

## SSH Sockets

To reduce number of SSH handshakes due to constant rsyncing between Local and Remote, enable SSH sockets on the local isntance

    mkdir /home/user/.ssh/sockets
    vim /home/user/.ssh/config

    Host <remote>
      TCPKeepAlive yes
      ServerAliveInterval 120
      Compression yes
      ControlMaster auto
      ControlPath ~/.ssh/sockets/%r@%h:%p
      ControlPersist yes
      ControlPersist 480m

    chmod 600 /home/user/.ssh/config
    chmod 770 /home/user/.ssh/sockets

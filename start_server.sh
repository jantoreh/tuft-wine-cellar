#!/bin/sh

if curl http://0.0.0.0:8000; then
    echo "server is up";
else
    echo "server is down";
    cd $HOME/wine && sudo -E env "PATH=$PATH" fastapi run main.py &
fi
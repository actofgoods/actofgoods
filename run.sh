#!/bin/bash
DIR="$( cd $( dirname "${BASH_SOURCE[0]}" ) && pwd )"


echo "Starting actofgoods"
source $DIR/venv/bin/activate
python3 $DIR/manage.py runserver
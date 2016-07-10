
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
message=test
echo "$message"
apt-get update
# install necessery programms through apt-get
apt-get install postgresql python3 python3-pip redis-server nginx postgresql-contrib libpq-dev
# install virtualenv through pip
pip3 install virtualenv
# create virtualenv
virtualenv $DIR/venv
#
. $DIR/venv/bin/activate
# install software through pip in virtualenv
pip3 install -r $DIR/requirements.txt
# virtualenv deactivate
deactivate
# copy conf file to nginx
cp $DIR/conf/actofgoods_nginx /etc/nginx/sites-available/actofgoods
# create sys link for sites-availbe
ln -s /etc/nginx/sites-available/actofgoods /etc/nginx/sites-enabled


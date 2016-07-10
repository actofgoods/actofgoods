
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
message=test
echo "$message"
apt-get update
# install necessery programms through apt-get
apt-get install postgresql python3 python3-pip redis-server nginx postgresql-contrib libpq-dev
# install virtualenv through pip
pip3 install virtualenv
# create virtualenv
virtualenv ./venv
#
. ./venv/bin/activate
# install software through pip in virtualenv
pip3 install -r ./requirements.txt
# virtualenv deactivate
deactivate
basename "$PWD"
# copy conf file to nginx
cp ./conf/actofgoods_nginx /etc/nginx/sites-available/actofgoods
# create sys link for sites-availbe
ln -s /etc/nginx/sites-available/actofgoods /etc/nginx/sites-enabled


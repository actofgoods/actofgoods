
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
message=test
echo "$message"
sudo apt-get update
# local
sudo locale-gen en_US.UTF-8
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
# install necessery programms through apt-get
sudo apt-get install postgresql python3 python3-pip redis-server nginx postgresql-contrib libpq-dev supervisor postgis virtualenv
# create virtualenv
virtualenv $DIR/venv
#
. $DIR/venv/bin/activate
# install software through pip in virtualenv
pip3 install -r $DIR/requirements.txt
# virtualenv deactivate
deactivate
# copy 
sudo cp $DIR/conf/actofgoods_nginx /etc/nginx/sites-available/actofgoods
# Copy file to nginx sites-availble
sudo sed -i "s!\${DIR}!$DIR!" /etc/nginx/sites-available/actofgoods
# create sys link for sites-availbe
sudo ln -sf /etc/nginx/sites-available/actofgoods /etc/nginx/sites-enabled
# enable site
sudo rm /etc/nginx/sites-enabled/default
# reload nginx
sudo service nginx reload
# copy file
cp $DIR/conf/actofgoods_server /etc/supervisor/conf.d/actofgoods.conf
# copy to supervisor
sudo sed -i "s!\${DIR}!$DIR!" $DIR/conf/actofgoods_server
# create db
sudo -u postgres psql -c "CREATE DATABASE actofgoods;"
sudo -u postgres psql -c "CREATE USER actofgoods WITH PASSWORD 'saft231';"
sudo -u postgres psql -c "Grant all privileges on database actofgoods to actofgoods;"
sudo -u postgres psql -c "ALTER USER actofgoods with superuser;"
# makemigrations
python3 $DIR/manage.py makemigrations
# migrate to database
python3 $DIR/manage.py migrate
# create logs
mkdir $DIR/logs
touch $DIR/logs/nginx-access.log
touch $DIR/logs/nginx-error.log
# load supervisord
sudo supervisord
# reread supervisor
sudo supervisorctl reread
# reload supervisor
sudo supervisorctl reload
# reload nginx
sudo service nginx reload

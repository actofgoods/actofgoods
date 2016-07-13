
# ------------------------------------------------------------
# Setup Environment
# ------------------------------------------------------------
#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
message=test
echo "$message"
sudo apt-get update
# install necessery programms through apt-get
sudo apt-get install postgresql python3 python3-pip redis-server nginx postgresql-contrib libpq-dev supervisor postgis
# install virtualenv through pip
pip3 install virtualenv
# create virtualenv
virtualenv $DIR/venv
#
. $DIR/venv/bin/activate
# install software through pip in virtualenv
pip3 install -r $DIR/requirements.txt
# virtualenv deactivate
# deactivate
# Copy file to nginx sites-availble
sed -e "s!\${DIR}!$DIR!" $DIR/conf/actofgoods_nginx > /etc/nginx/sites-available/actofgoods
# create sys link for sites-availbe
sudo ln -sf /etc/nginx/sites-available/actofgoods /etc/nginx/sites-enabled
# enable site
sudo rm /etc/nginx/sites-enabled/default
# reload nginx
sudo service nginx reload
# copy to supervisor
sed -e "s!\${DIR}!$DIR!" $DIR/conf/actofgoods_server > /etc/supervisor/conf.d/actofgoods.conf
# create db
sudo -u postgres
sudo -u postgres psql -c "CREATE USER actofgoods WITH PASSWORD 'saft231';"
sudo -u postgres psql -c "Grant all privileges on database actofgoods to actofgoods;"
# makemigrations
python3 $DIR/manage.py makemigrations
# migrate to database
python3 $DIR/manage.py migrate
# load supervisord
sudo supervisord
# reread supervisor
sudo supervisorctl reread
# reload supervisor
sudo supervisorctl reload

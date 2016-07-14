[![Stories in Ready](https://badge.waffle.io/actofgoods/actofgoods.png?label=ready&title=Ready)](https://waffle.io/actofgoods/actofgoods)
# actofgoods
Postgressql siehe hier:https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04  
Details zu datenbank stehen in settings.py

#Automatic Installation for ubuntu/debian:

Use install_script.sh to install automatic and deploy the server  
If you want to use a different Database system, you have to change the settings.py and the install script.

#Manual Installation:

Install from your package manager (for example yum) following packages:

Database:
postgresql
postgis
postgresql-contrib
libpq-dev

Python:
python3
python3-pip

Redis (Chat):
redis-server

Nginx (Reverse proxy):
nginx

supervisor (running python server):
supervisor

PACKAGE-INSTALL:
pip install -r requirements.txt

virtualenv

Now create a virtualenv:
Run following command in the directory of the project:
virtualenv venv
If you want to install it somewhere else, you have to change run.bash to the correct directory

Install python package:  
All at wants:  
pip3 install -r requirments

deactivate the virtualenv  

Create database and user for database:  
sudo -u postgres psql -c "CREATE DATABASE actofgoods;"  
sudo -u postgres psql -c "CREATE USER actofgoods WITH PASSWORD 'saft231';"  
sudo -u postgres psql -c "Grant all privileges on database actofgoods to actofgoods;"  
sudo -u postgres psql -c "ALTER USER actofgoods with superuser;"  
If you changed settings.py the database change the commands to your needs  

Copy file conf/actofgoods_nginx to the installtion of nginx inside the nginx-availble and change the name to actofgoods.  
Change ${DIR} to right way to your copy of the project  
Now create a systemlink of actofgoods in the sites-enabled  
Now reload nginx  

Copy file conf/actofgoods_server to superviser/conf.d  
Change name to actofgoods.conf  
Change ${DIR} in the file to way to run.bash  
Reload supervisor  

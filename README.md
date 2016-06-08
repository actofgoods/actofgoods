[![Stories in Ready](https://badge.waffle.io/actofgoods/actofgoods.png?label=ready&title=Ready)](https://waffle.io/actofgoods/actofgoods)
# actofgoods  
Postgressql siehe hier:https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04  
Details zu datenbank stehen in settings.py


#Requirements:

PACKAGE-INSTALL:
pip install -r requirements.txt


ALTERNATIVE:

pip install requests

pip install django-nocaptcha-recaptcha

If you got problems with database try:

python manage.py makemigrations basics

=== CHANNEL install ===

pip install -U channels

=== Redis Layer install ===

pip install asgi_redis

wget http://download.redis.io/redis-stable.tar.gz

tar xvzf redis-stable.tar.gz

cd redis-stable

make

sudo make install

#Database

sudo su - postgres

psql

CREATE DATABASE actofgoods
- New database will be created

DROP DATABASE actofgoods
- Database will be droped

GRANT ALL PRIVILEGES ON DATABASE actofgoods TO actofgoods;

ALTER USER django CREATEDB;
- will give the user permission to create new databases.

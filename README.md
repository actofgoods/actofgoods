[![Stories in Ready](https://badge.waffle.io/actofgoods/actofgoods.png?label=ready&title=Ready)](https://waffle.io/actofgoods/actofgoods)
# actofgoods  
Postgressql siehe hier:https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04  
Details zu datenbank stehen in settings.py


#Requirements:

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


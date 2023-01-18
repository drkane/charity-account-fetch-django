


```sh
# create app
dokku apps:create charity-account-fetch

# postgres
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres
dokku postgres:create account-fetch-db
dokku postgres:link account-fetch-db charity-account-fetch

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
dokku elasticsearch:create account-fetch-es
dokku elasticsearch:link account-fetch-es charity-account-fetch

# letsencrypt
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart --global DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt:enable charity-account-fetch
dokku letsencrypt:cron-job --add

# set secret key
# To generate use:
# `python -c "import secrets; print(secrets.token_urlsafe())"`
dokku config:set --no-restart charity-account-fetch SECRET_KEY='<insert secret key>'

# setup hosts
dokku config:set charity-account-fetch --no-restart DEBUG=false ALLOWED_HOSTS="hostname.example.com"

# import initial charity data
dokku run charity-account-fetch python ./manage.py import_oscr
dokku run charity-account-fetch python ./manage.py import_ccew
dokku run charity-account-fetch python ./manage.py import_ccni
dokku run charity-account-fetch python ./manage.py update_charities

# create superuser account
dokku run charity-account-fetch python manage.py createsuperuser

# create cache table
dokku run charity-account-fetch python manage.py createcachetable

# create the elasticsearch index
dokku run charity-account-fetch python manage.py search_index --create

# setup account directory
dokku storage:ensure-directory charity-account-fetch
dokku storage:mount charity-account-fetch /var/lib/dokku/data/storage/charity-account-fetch:/app/storage
dokku config:set charity-account-fetch --no-restart MEDIA_ROOT=/app/storage/media/

# setup ocrmypdf
sudo dokku plugin:install https://github.com/dokku-community/dokku-apt apt
```


```
git remote add dokku dokku@SERVER_HOST:charity-account-fetch
git push dokku main
```
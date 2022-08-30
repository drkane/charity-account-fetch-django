


```sh
# create app
dokku apps:create dj-account-fetch

# postgres
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres
dokku postgres:create account-fetch-db
dokku postgres:link account-fetch-db ftc

# elasticsearch
sudo dokku plugin:install https://github.com/dokku/dokku-elasticsearch.git elasticsearch
dokku elasticsearch:create account-fetch-es
dokku elasticsearch:link account-fetch-es dj-account-fetch

# letsencrypt
sudo dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
dokku config:set --no-restart ftc DOKKU_LETSENCRYPT_EMAIL=your@email.tld
dokku letsencrypt:enable dj-account-fetch
dokku letsencrypt:cron-job --add

# set secret key
# To generate use:
# `python -c "import secrets; print(secrets.token_urlsafe())"`
dokku config:set --no-restart dj-account-fetch SECRET_KEY='<insert secret key>'

# setup hosts
dokku config:set dj-account-fetch --no-restart DEBUG=false ALLOWED_HOSTS="hostname.example.com"

# import initial charity data
dokku run dj-account-fetch python ./manage.py import_oscr
dokku run dj-account-fetch python ./manage.py import_ccew
dokku run dj-account-fetch python ./manage.py import_ccni
dokku run dj-account-fetch python ./manage.py update_charities

# create superuser account
dokku run dj-account-fetch python manage.py createsuperuser

# create the elasticsearch index
python manage.py search_index --create

# setup account directory
dokku storage:ensure-directory dj-account-fetch
dokku storage:mount dj-account-fetch /var/lib/dokku/data/storage/dj-account-fetch:/app/storage
dokku config:set dj-account-fetch --no-restart MEDIA_ROOT=/app/storage/media/
```


```
git remote add dokku dokku@SERVER_HOST:ftc
git push dokku main
```
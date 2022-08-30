


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
dokku letsencrypt dj-account-fetch
dokku letsencrypt:cron-job --add

# set secret key
# To generate use:
# `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
dokku config:set --no-restart dj-account-fetch SECRET_KEY='<insert secret key>'
```


```
git remote add dokku dokku@SERVER_HOST:ftc
git push dokku main
```
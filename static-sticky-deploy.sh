#!/bin/sh

git clone git@github.com:svsticky/static-sticky.git
cd static-sticky

# probably we don't want to copy the keys in the .env file manually
# for now we asume this is the case

npm run build

# $1 should be the correct deploy folder, either dev.svsticky.nl or svsticky.nl, depending on the environment
cp public /var/www/static-sticky/$1

# cleanup
cd ..
rm -rf static-sticky
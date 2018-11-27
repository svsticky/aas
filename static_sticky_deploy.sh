git clone git@github.com:svsticky/static-sticky.git
cd static-sticky

# probably we don't want to copy the keys in the .env file manually
# for now we asume this is the case

npm run build

cp public /var/www/static-sticky
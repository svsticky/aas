# AAS
A webhook listener for use at Study Association Sticky, written as a Flask application.

Its current use is to make automatic deployment possible of [our website][static-sticky] in our [production environment][sadserver], triggered by GitHub pushes or changes in the Contentful CMS it uses.

# Usage
This project requires Python 3.6+ and [`pipenv`][pipenv].

## Development
```
# Install the dependencies of `aas` as specified in Pipfile.lock
$ pipenv sync --dev
# Use the provided sample.env to create a .env file and populate the environment variables
$ cp sample.env .env
$ vim .env
# Run the development server
$ pipenv run server
```
If you want to update the dependencies, following the version constraints in Pipfile, run `pipenv install --dev`.

## Production
The dependencies include `gunicorn`, which is a WSGI server for use in production.
You can use the following commands as a simple example:
```
$ pipenv sync
$ pipenv run gunicorn aas:aas
```
This binds `gunicorn` to http://localhost:8000/. You should place a reverse proxy, like `nginx`, in front of this.

To set this up in our own production environment, we use some [Ansible tasks][sadserver-aas].

# Testing consumption of webhooks in development
To make the development server temporarily available for webhook consumers in the outside world (e.g. GitHub), you can use [`ngrok`][ngrok].
If you're running `snap`, you can install it using `snap install ngrok`.

When installed, you can [run](#development) `aas` in one terminal and in another terminal run `ngrok http 5000` (`5000` being the default port Flask's development server binds to).

 [static-sticky]: http://github.com/svsticky/static-sticky
 [sadserver]: https://github.com/svsticky/sadserver/
 [pipenv]: https://github.com/pypa/pipenv
 [sadserver-aas]: https://github.com/svsticky/sadserver/blob/master/ansible/tasks/aas.yml
 [ngrok]: https://ngrok.com/

# AAS
A webhook listener for use at Study Association Sticky, written as a Flask application.

Its current use is to make automatic deployment to [our server][sadserver]
possible of [our website][static-sticky] and our [sign-up page][intro],
triggered by GitHub pushes or changes in the Contentful CMS it uses.

This project can be extended for other webhook processing.

# Usage
This project requires uv to install the right python version and packages in a virtual environment.

## Development

```console
# Use the provided 'sample.config.json' to create a 'config.json'
# file and adjust it to your needs. (See 'Configuration' section)
cp sample.config.json config.json
vim config.json
# Run the development server using uv
uv run aas.py
```

## Configuration

Aas is build to support multiple types of webhooks.
For every type of endpoint you can define a class (webhook handler)
which will handle all requests to that endpoint. For example, you
can define a webhook handler which runs a systemd service on incoming webhooks.

To abstract your endpoints from this implementation, aas loads up your endpoint
config from `config.json`. This json contains a mappings from endpoints to
webhook handlers. This means that if you ever want to add an endpoint, you simply
expand the `config.json`.

## Production
The dependencies include `gunicorn`, which is a WSGI server for use in production.
You can use the following commands as a simple example:

```
uv run gunicorn aas:aas
```

This binds `gunicorn` to `http://localhost:8000/`. You should place a reverse proxy,
like `nginx`, in front of this.

To set this up in our own production environment, we use some [Ansible tasks][sadserver-aas].

# Testing consumption of webhooks in development

To make the development server temporarily available for webhook consumers in
the outside world (e.g. GitHub), you can use [`ngrok`][ngrok].

To use it, you can [run](#development) `aas` in one terminal and in another terminal
run `ngrok http 5000` (`5000` being the default port Flask's development server binds to).

 [static-sticky]: http://github.com/svsticky/static-sticky
 [intro]: http://github.com/svsticky/intro-website
 [sadserver]: https://github.com/svsticky/sadserver/
 [sadserver-aas]: https://github.com/svsticky/sadserver/blob/master/ansible/tasks/aas.yml
 [ngrok]: https://ngrok.com/

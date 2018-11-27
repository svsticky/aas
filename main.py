from flask import Flask, request, Response, abort
from flask_restful import Api, Resource
from hashlib import sha1
import hmac
import json
import subprocess

app = Flask(__name__)
app.debug = True
api = Api(app)

class GitHub(Resource):
    # Share this secret with GitHub to authenticate this hook
    SECRET=b'hunter2'

    def post(self):
        ## Check authentication ##
        # remove the sha1= prefix of the signature
        # TODO: find more elegant way to do this
        signature = request.headers.get('X-Hub-Signature')[5:]
        
        if not hmac.compare_digest(signature, hmac.new(self.SECRET, request.get_data(), sha1).hexdigest()):
            abort(401)
        
        # TODO: replace variable by actual environment variable
        subprocess.call(['./static-sticky-deploy.sh', "dev.svsticky.nl"])

        return Response(status=200)

class Sentry(Resource):
    # Share this secret with Sentry to authenticate this hook
    SECRET=b'hunter2'

    def post(self):
        ## TODO: find out if Sentry supports authenticated webhooks
        # btw this is quite important since we're 'eval'ing the input
        
        ## TODO: do something with the payload
        # payload is found in request.form

        # TODO: check if keys actually exist
        print(json.dumps(request.get_json()['event']['exception']['values'])) # DEBUG


        return Response(status=200)        

api.add_resource(GitHub, '/webhook/github')
api.add_resource(Sentry, '/webhook/sentry')
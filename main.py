from flask import Flask, request, Response, abort
from flask_restful import Api, Resource
from hashlib import sha1
import hmac

app = Flask(__name__)
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
        
        ## TODO: do something with the payload
        # payload is found in request.form

        return Response(status=200)

class Sentry(Resource):
    # Share this secret with Sentry to authenticate this hook
    SECRET=b'hunter2'

    def post(self):
        ## TODO: find out if Sentry supports authenticated webhooks
        
        ## TODO: do something with the payload
        # payload is found in request.form

        return Response(status=200)        

api.add_resource(GitHub, '/webhook/github')
api.add_resource(Sentry, '/webhook/sentry')
from flask import Flask, request, Response, abort
from flask_restful import Api, Resource
from hashlib import sha1
import hmac
import json
import subprocess
import os

app = Flask(__name__)
app.debug = True
api = Api(app)


class GitHub(Resource):
    # Share this secret with GitHub to authenticate this hook
    SECRET = os.environ["GITHUB_SECRET"].encode()

    def post(self):
        ## Check authentication ##
        # remove the sha1= prefix of the signature
        # TODO: find more elegant way to do this
        signature = request.headers.get("X-Hub-Signature")[5:]

        if not hmac.compare_digest(
            signature, hmac.new(self.SECRET, request.get_data(), sha1).hexdigest()
        ):
            abort(401)
        
        directory = os.environ["DEPLOY_DIRECTORY"]
        subprocess.call(['./static-sticky-deploy.sh', directory])

        return Response(status=200)


class Sentry(Resource):
    # Share this secret with Sentry to authenticate this hook

    def post(self):
        # TODO: check if keys actually exist
        data = request.get_json()

        traceback = json.dumps(data["event"]["exception"]["values"], indent = 4)
        message = data["message"]
        failing_request = data["event"]["request"]

        #DEBUG
        print(message)
        print(failing_request)

        # TODO: create GitHub issue

        return Response(status=200)


api.add_resource(GitHub, "/webhook/github")
SECRET_ENDPOINT = os.environ["SENTRY_SECRET_ENDPOINT"]
api.add_resource(Sentry, "/webhook/sentry/" + SECRET_ENDPOINT)

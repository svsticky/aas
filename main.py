import concurrent.futures
import hashlib
import hmac
import json
import subprocess
import os

from flask import Flask, request, Response, abort
from flask_restful import Api, Resource


executor = concurrent.futures.ThreadPoolExecutor(2)


def deploy_static_sticky():
    deploy_service = os.getenv("DEPLOY_SERVICE")
    # make sure this command is added to the sudoers file, otherwise it will fail
    subprocess.run(["systemctl", "start", "--no-block", deploy_service])


class GitHub(Resource):
    # Share this secret with GitHub to authenticate this hook
    SECRET = os.environ["GITHUB_SECRET"].encode()

    def post(self):
        ## Check authentication ##
        # remove the sha1= prefix of the signature
        # TODO: find more elegant way to do this
        signature = request.headers.get("X-Hub-Signature")[5:]

        if not hmac.compare_digest(
            signature,
            hmac.new(self.SECRET, request.get_data(), hashlib.sha1).hexdigest(),
        ):
            abort(401)

        executor.submit(deploy_static_sticky)

        return Response(status=200)

class Contentful(Resource):
    def post(self):
        executor.submit(deploy_static_sticky)
        return Response(status=200)


if __name__ == "__main__":
    app = Flask(__name__)
    app.debug = True
    api = Api(app)

    contentful_endpoint = os.getenv("CONTENTFUL_SECRET_ENDPOINT")

    api.add_resource(GitHub, "/webhook/github")
    api.add_resource(Contentful, "/webhook/contentful/" + contentful_endpoint)

    app.run()

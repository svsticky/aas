import concurrent.futures
import hashlib
import hmac
import json
import subprocess
import os

import requests
from flask import Flask, request, Response, abort
from flask_restful import Api, Resource


def deploy_static_sticky():
    deploy_service = os.getenv("DEPLOY_SERVICE")
    # Make sure the user running this has root privileges to start this command, e.g. by adding it to a sudoers file
    subprocess.run(
        [
            "sudo",
            "/usr/bin/systemd-run",
            "--no-block",
            "--property",
            f"After={deploy_service}",
            "--",
            "systemctl",
            "start",
            deploy_service,
        ],
        check=True,
    )


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

        response_payload = request.get_json()

        deploy_static_sticky()


aas = Flask(__name__)
aas_api = Api(aas, catch_all_404s=True)

contentful_endpoint = os.getenv("CONTENTFUL_SECRET_ENDPOINT", "missing")

aas_api.add_resource(GitHub, "/webhook/github")

if __name__ == "__main__":
    aas.run()

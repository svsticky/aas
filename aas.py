import concurrent.futures
import hashlib
import hmac
import json
import subprocess
import os

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


def github_authenticated(secret):
    # remove the sha1= prefix of the signature
    signature = request.headers.get("X-Hub-Signature")[5:]

    return hmac.compare_digest(
        signature,
        hmac.new(secret, request.get_data(), hashlib.sha1).hexdigest(),
    )


class GitHub(Resource):
    # Share this secret with GitHub to authenticate this hook
    SECRET = os.environ["GITHUB_SECRET_STATIC_STICKY"].encode()

    def post(self):
        if not github_authenticated(self.SECRET):
            abort(401)

        response_payload = request.get_json()

        if "ref" in response_payload:
            pushed_branch = response_payload["ref"]
            deploy_branch = os.environ["DEPLOY_REF"]

            if pushed_branch == "refs/heads/" + deploy_branch:
                deploy_static_sticky()
                return Response(status=200)
            else:
                return Response(status=202)
        else:
            abort(400)


class Contentful(Resource):
    def post(self):
        deploy_static_sticky()
        return Response(status=200)


class Stickypedia(Resource):
    # Share this secret with GitHub to authenticate this hook
    SECRET = os.environ["GITHUB_SECRET"].encode()

    def post(self):
        if not github_authenticated(self.SECRET):
            abort(401)

        # Make sure the user running this has the rights to call the script
        subprocess.call([os.getenv("STICKYPEDIA_PULL_SCRIPT")])
        return Response(status=200)


aas = Flask(__name__)
aas_api = Api(aas, catch_all_404s=True)

contentful_endpoint = os.getenv("CONTENTFUL_SECRET_ENDPOINT")

aas_api.add_resource(GitHub, "/webhook/github")
aas_api.add_resource(Contentful, "/webhook/contentful/" + contentful_endpoint)
aas_api.add_resource(Stickypedia, "/webhook/stickypedia")

if __name__ == "__main__":
    aas.run()

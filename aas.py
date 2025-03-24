import hashlib
import hmac
import json
import subprocess

from flask import Flask, request, abort
from flask_restful import Api, Resource

def run_systemd(service_name):
    """Runs a single systemd service on the system"""
    # Make sure the user running this has root privileges to start this command,
    # e.g. by adding it to a sudoers file for this specific command
    subprocess.run(
        [
            "sudo",
            "/usr/bin/systemd-run",
            "--no-block",
            "--property",
            f"After={service_name}",
            "--",
            "systemctl",
            "start",
            service_name,
        ],
        check=True,
    )

class RunSystemdHandler(Resource):
    """
    Run a specified systemd service on incoming authenticated webhooks.
    Requests are authenticated with a pre-shared key, known to both Aas and
    the calling party.
    """

    def __init__(self, service_name, preshared_key):
        super().__init__()
        self.service_name = service_name
        self.preshared_key = preshared_key.encode()
        self.__name__ = f'RunSystemdHandler {service_name}'

    def post(self):
        ## Check authentication ##
        # remove the sha1= prefix of the signature
        # TODO: find more elegant way to do this
        signature = request.headers.get("X-Hub-Signature")[5:]

        # Test if webhook is authenticated with known secret
        if not hmac.compare_digest(
            signature,
            hmac.new(self.preshared_key, request.get_data(), hashlib.sha1).hexdigest(),
        ):
            abort(401)

        run_systemd(self.service_name)


def load_webhooks(api):
    """Dynamically sets up all webhook handlers based on the config.json"""
    with open('config.json') as f: config = json.load(f)

    # Load all RunSystemd webhook handlers
    for webhook in config["webhookHandlers"]["runSystemd"]:
        handler = RunSystemdHandler(webhook["serviceName"], webhook["pre-sharedKey"])
        api.add_resource(handler, webhook["endpoint"])


aas = Flask(__name__)
aas_api = Api(aas, catch_all_404s=True)
load_webhooks(aas_api)

if __name__ == "__main__":
    aas.run()

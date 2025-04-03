import hashlib
import hmac
import json
import subprocess

from flask import Flask, request, abort
from flask_restful import Api, Resource

def run_systemd(service_name):
    """Runs a single systemd service on the system."""

    print(f"Starting systemd service '{service_name}'")

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

def create_systemd_handler(service_name, preshared_key):
    """
    This function is a wrapper for Flask, for flask cannot assign an instance of a class
    to an endpoint, and instead wants to create an instance on its own. We thus tell him here how!
    """

    instance_name = f'RunSystemdHandler {service_name}'
    class RunSystemdHandler(Resource):
        """
        Run a specified systemd service on incoming authenticated webhooks.
        Requests are authenticated with a pre-shared key, known to both Aas and
        the calling party.
        """

        def __init__(self):
            super().__init__()
            self.service_name = service_name
            self.preshared_key = preshared_key.encode()
            self.__name__ = instance_name # Needed for Flask, but useful anyway
            print(f"  Created handler '{self.__name__}'")

        def post(self):
            print(f"{self.__name__}: responding to webhook!")

            ## Check authentication ##
            signature_header_name = "X-Hub-Signature"
            signature_header = request.headers.get(signature_header_name)
            if signature_header is None or len(signature_header) == 0:
                print(f"{self.__name__}: Warning: The webhook request did not provide a '{signature_header_name}' header.")
                print(f"{self.__name__}:          Responding with 402.")
                abort(401) # TODO make this 402, currently we have no handler for 402

            # remove the sha1= prefix of the signature
            # TODO: find more elegant way to do this
            signature = signature_header[5:] # Signature is an HMAC hexdigest of the request body with preshared key

            # Test if webhook is authenticated with known secret
            if not hmac.compare_digest(
                signature, # Already hashed like below
                hmac.new(self.preshared_key, request.get_data(), hashlib.sha1).hexdigest(),
            ):
                print(f'{self.__name__}: Warning: The webhook request could not authenticate itself.')
                print(f"{self.__name__}:          The signature received ended with '{signature[-4:]}'")
                abort(401)

            print(f"{self.__name__}: Authenticated! Starting systemd service.")

            run_systemd(self.service_name)
            return('Yoink!')

    RunSystemdHandler.__name__ = instance_name # Prevents duplicate assignments to same endpoint (Flask stuff)
    return RunSystemdHandler


def load_webhooks(api):
    """Dynamically sets up all webhook handlers based on the 'config.json'."""
    with open('config.json') as f: config = json.load(f)
    print('Parsing the following config:')
    print(config)
    print('')

    # Load all RunSystemd webhook handlers
    for webhook in config["webhookHandlers"]["runSystemd"]:
        service_name = webhook["serviceName"]
        endpoint = webhook["endpoint"]
        pre_shared_key = webhook["pre-sharedKey"]

        print(f"Subscribing a systemd handler to endpoint '{endpoint}' for service '{service_name}'")
        print(f"  The webhook expects authentication with a pre-shared key ending with '{pre_shared_key[-4:]}'")
        api.add_resource(create_systemd_handler(service_name, pre_shared_key), endpoint)

if __name__ == "__main__":
    print('Aas is starting...\n')

    aas = Flask(__name__)
    aas_api = Api(aas, catch_all_404s=True)
    load_webhooks(aas_api)

    print('\nBegining to listen to webhooks!\n')
    aas.run()

    print('\nAas is closing...')

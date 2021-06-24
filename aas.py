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


class Pretix(Resource):
    TOKEN = os.environ["PRETIX_TOKEN"]

    def post(self):
        payload = request.get_json()

        url = (
            f'https://pretix.svsticky.nl/api/v1/organizers/{payload["organizer"]}/'
            f'events/{payload["event"]}/orders/{payload["code"]}/'
        )

        response = requests.get(url, headers={"Authorization": f"Token {self.TOKEN}"})
        data = response.json()

        position = data["positions"][0]

        answers = {}

        for answer in position["answers"]:
            identifier = answer["question_identifier"]
            value = answer["answer"]

            answers[identifier] = value

        if answers.get("aeskwadraat_signup") != "True":
            return Response(status=200)

        aes_studie = {
            "Informatica": "IC",
            "Informatiekunde": "IK",
            "Dubbele bachelor Informatica/Informatiekunde": "IC/IK",
        }.get(answers.get("studies"))

        voornaam = position["attendee_name_parts"]["given_name"]
        achternaam = position["attendee_name_parts"]["family_name"]

        email = data["email"]

        payload = {
            "email": email,
            "voornaam": voornaam,
            "tussenvoegsel": "",
            "achternaam": achternaam,
            "geboortedatum": answers.get("geboortedatum"),
            "studentnummer": answers.get("studentnummer"),
            "straat": "unknown",
            "huisnummer": "unknown",
            "postcode": "unknown",
            "plaats": "unknown",
            "mobiel": data["phone"],
            "studie": aes_studie,
        }

        if data.get("testmode"):
            print(f"Got a test mode signup: {payload}")
        else:
            response = requests.get(
                "https://www.a-eskwadraat.nl/Leden/Intro/Aanmelden", params=payload
            )

            response.raise_for_status()

        return Response(status=200)


aas = Flask(__name__)
aas_api = Api(aas, catch_all_404s=True)

contentful_endpoint = os.getenv("CONTENTFUL_SECRET_ENDPOINT", "missing")

aas_api.add_resource(GitHub, "/webhook/github")
aas_api.add_resource(Contentful, "/webhook/contentful/" + contentful_endpoint)
aas_api.add_resource(Pretix, "/webhook/pretix")

if __name__ == "__main__":
    aas.run()
